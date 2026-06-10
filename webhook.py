from flask import Flask, request, jsonify
import logging
import json
from datetime import datetime, timedelta
import os
import threading
import requests

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Cache para evitar processamento duplicado por evento
processed_events = {}  # {transaction_id: timestamp}
transaction_lock = threading.Lock()

# ==================== FUNÇÕES AUXILIARES COMPARTILHADAS ====================

def load_credenciais():
    """Carrega credenciais do arquivo JSON"""
    try:
        with open('settings/credenciais.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ Erro ao carregar credenciais: {e}")
        return {}

def load_users():
    """Carrega dados dos usuários"""
    try:
        with open('database/users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ Erro ao carregar users.json: {e}")
        return {"users": []}

def save_users(data):
    """Salva dados dos usuários"""
    try:
        with open('database/users.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao salvar users.json: {e}")
        return False

def send_telegram_message(chat_id, text, parse_mode='Markdown'):
    """Envia mensagem via Telegram"""
    try:
        creds = load_credenciais()
        bot_token = creds.get('api-bot')
        if not bot_token:
            logger.error("Token do bot não encontrado")
            return False
        
        url = f"https://api.telegram.org/bot8681198091:AAGtaDU2EfJJkIXGogaX42aqeckJqEKZ9oM/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Mensagem enviada para {chat_id}")
            return True
        else:
            logger.error(f"❌ Erro ao enviar mensagem: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem Telegram: {e}")
        return False

def delete_telegram_message(chat_id, message_id):
    """Deleta mensagem do Telegram"""
    try:
        creds = load_credenciais()
        bot_token = creds.get('api-bot')
        if not bot_token:
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/deleteMessage"
        data = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"❌ Erro ao deletar mensagem: {e}")
        return False

# ==================== FUNÇÕES ZUCPAY ====================

@app.route('/webhook/zucpay-sms', methods=['POST'])
def zucpay_sms_webhook():
    """Webhook para receber callbacks do Zucpay para recarga de saldo SMS"""
    try:
        raw_data = request.get_data()
        logger.info(f"📨 Zucpay - Dados brutos recebidos: {raw_data}")
        
        # Zucpay envia JSON
        data = request.get_json(silent=True) or {}
        logger.info(f"📨 Zucpay - Dados parseados como JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")

        if not data:
            logger.error("❌ Zucpay - Payload inválido ou vazio")
            return jsonify({'error': 'Payload inválido'}), 400

        logger.info(f"📨 Zucpay - Chaves disponíveis: {list(data.keys())}")

        # Extrair dados do webhook Zucpay
        transaction_id = data.get('transaction_id') or data.get('data', {}).get('transaction_id')
        external_id = data.get('external_id') or data.get('data', {}).get('external_id')
        status = data.get('status') or data.get('data', {}).get('status')
        amount = data.get('amount') or data.get('data', {}).get('amount')
        gateway = data.get('gateway') or data.get('data', {}).get('gateway')
        
        logger.info(f"🔍 Zucpay - Transaction ID: '{transaction_id}'")
        logger.info(f"🔍 Zucpay - External ID: '{external_id}'")
        logger.info(f"🔍 Zucpay - Status: '{status}'")
        logger.info(f"🔍 Zucpay - Amount: {amount}")
        logger.info(f"🔍 Zucpay - Gateway: {gateway}")

        # Usar transaction_id como identificador principal
        payment_id = transaction_id or external_id
        
        if not payment_id:
            logger.error("❌ Zucpay - ID do pagamento não encontrado")
            return jsonify({'error': 'transaction_id obrigatório'}), 400

        # Controle de duplicatas
        with transaction_lock:
            cache_key = f"{payment_id}_{status}"
            if cache_key in processed_events:
                logger.warning(f"⚠️ Zucpay - Evento duplicado ignorado: {payment_id} - {status}")
                return jsonify({'ok': True, 'payment_id': payment_id, 'status': status})

            processed_events[cache_key] = datetime.now()

            # Limpar cache antigo (mais de 1 hora)
            current_time = datetime.now()
            expired_keys = [
                key for key, timestamp in processed_events.items() 
                if isinstance(timestamp, datetime) and (current_time - timestamp) > timedelta(hours=1)
            ]
            for key in expired_keys:
                del processed_events[key]

        # Extrair metadados adicionais
        metadata = {
            'gateway': gateway,
            'provider': 'Zucpay',
            'raw_data': data
        }

        result = process_zucpay_event(
            payment_id=payment_id,
            status=status,
            amount=amount,
            metadata=metadata,
            data=data
        )

        if result.get('success'):
            return jsonify({'ok': True, 'payment_id': payment_id, 'status': status})
        else:
            with transaction_lock:
                cache_key = f"{payment_id}_{status}"
                if cache_key in processed_events:
                    del processed_events[cache_key]
            return jsonify({'error': result.get('error', 'Erro desconhecido')}), 400

    except Exception as e:
        logger.error(f"❌ Zucpay - Erro: {str(e)}", exc_info=True)
        return jsonify({'error': 'Erro interno'}), 500

def process_zucpay_event(payment_id, status, amount, metadata, data):
    """Processa eventos do Zucpay"""
    logger.info(f"🔄 Zucpay - Processando {status} para {payment_id}")
    
    try:
        users_data = load_users()
        
        payment_found = None
        user_id = None
        
        # Buscar pagamento pelo ID da transação
        logger.info(f"🔍 Zucpay - Buscando pagamento {payment_id} no users.json")
        
        for user_data in users_data.get('users', []):
            for payment in user_data.get('pagamentos', []):
                payment_id_registro = payment.get('id_pagamento')
                logger.debug(f"Comparando: {payment_id_registro} com {payment_id}")
                
                if payment_id_registro == payment_id:
                    payment_found = payment
                    user_id = int(user_data['id'])
                    logger.info(f"✅ Zucpay - Pagamento encontrado! Usuário: {user_id}")
                    break
            if payment_found:
                break
        
        if not payment_found:
            logger.error(f"❌ Zucpay - Pagamento {payment_id} não encontrado no users.json")
            return {'success': False, 'error': 'Pagamento não encontrado'}
        
        logger.info(f"✅ Zucpay - Processando pagamento do usuário {user_id}")
        
        # Mapear status do Zucpay para status internos
        if status in ['pending', 'waiting', 'created']:
            return handle_zucpay_pending(payment_id, status, data, users_data, user_id, payment_found)
        elif status in ['completed', 'confirmed', 'paid', 'success']:
            return handle_zucpay_paid(payment_id, status, data, users_data, user_id, payment_found, amount)
        elif status in ['cancelled', 'canceled', 'expired']:
            return handle_zucpay_cancelled(payment_id, status, data, users_data, user_id, payment_found)
        elif status in ['refunded', 'refund']:
            return handle_zucpay_refunded(payment_id, status, data, users_data, user_id, payment_found, amount)
        elif status in ['failed', 'error']:
            return handle_zucpay_failed(payment_id, status, data, users_data, user_id, payment_found)
        else:
            logger.info(f"📝 Zucpay - Status {status} não processado")
            # Mesmo assim, atualiza o status no registro
            for user_data in users_data.get('users', []):
                if user_data['id'] == user_id:
                    for p in user_data.get('pagamentos', []):
                        if p.get('id_pagamento') == payment_id:
                            p['status'] = status
                            p['updated_at'] = datetime.now().isoformat()
                            break
                    break
            save_users(users_data)
            return {'success': True, 'message': f'Status {status} registrado'}
            
    except Exception as e:
        logger.error(f"❌ Zucpay - Erro: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}

def handle_zucpay_pending(payment_id, status, data, users_data, user_id, payment):
    """Pagamento pendente Zucpay"""
    try:
        for user_data in users_data.get('users', []):
            if user_data['id'] == user_id:
                for p in user_data.get('pagamentos', []):
                    if p.get('id_pagamento') == payment_id:
                        p['status'] = 'pending'
                        p['updated_at'] = datetime.now().isoformat()
                        break
                break
        
        save_users(users_data)
        logger.info(f"✅ Zucpay - Status atualizado para pending: {payment_id}")
        
        notify_admin_payment_created(payment_id, user_id, payment, 'Zucpay')
        return {'success': True}
    except Exception as e:
        logger.error(f"❌ Zucpay - Erro pending: {e}")
        return {'success': False, 'error': str(e)}

def handle_zucpay_paid(payment_id, status, data, users_data, user_id, payment, amount):
    """Pagamento aprovado Zucpay - adicionar saldo"""
    try:
        # Usar o valor do pagamento ou o amount recebido
        valor_pagamento = float(payment.get('valor', amount or 0))
        
        creds = load_credenciais()
        bonus_pix = creds.get('bonus_pix', 0)
        bonus_pix_min = creds.get('bonus_pix_min', 0)
        
        saldo_adicional = valor_pagamento
        if valor_pagamento >= bonus_pix_min and bonus_pix > 0:
            bonus_valor = valor_pagamento * (bonus_pix / 100)
            saldo_adicional += bonus_valor
            logger.info(f"🎁 Zucpay - Bônus aplicado: +R${bonus_valor:.2f}")
        
        novo_saldo = 0
        for user_data in users_data.get('users', []):
            if user_data['id'] == user_id:
                saldo_atual = user_data.get('saldo', 0)
                novo_saldo = saldo_atual + saldo_adicional
                user_data['saldo'] = novo_saldo
                
                for p in user_data.get('pagamentos', []):
                    if p.get('id_pagamento') == payment_id:
                        p['status'] = 'approved'
                        p['updated_at'] = datetime.now().isoformat()
                        break
                
                user_data['total_pagos'] = user_data.get('total_pagos', 0) + valor_pagamento
                logger.info(f"✅ Zucpay - Saldo atualizado: R${saldo_atual:.2f} -> R${novo_saldo:.2f}")
                break
        
        save_users(users_data)
        
        # Deletar mensagens do QR code
        delete_qr_code_messages(user_id, payment_id)
        
        # Notificações
        notify_user_payment_approved(user_id, valor_pagamento, saldo_adicional, novo_saldo)
        notify_admin_payment_approved(payment_id, user_id, payment, valor_pagamento, saldo_adicional, 'Zucpay', data)
        
        return {'success': True}
    except Exception as e:
        logger.error(f"❌ Zucpay - Erro paid: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}

def handle_zucpay_cancelled(payment_id, status, data, users_data, user_id, payment):
    """Pagamento cancelado Zucpay"""
    try:
        for user_data in users_data.get('users', []):
            if user_data['id'] == user_id:
                for p in user_data.get('pagamentos', []):
                    if p.get('id_pagamento') == payment_id:
                        p['status'] = 'cancelled'
                        p['updated_at'] = datetime.now().isoformat()
                        break
                break
        
        save_users(users_data)
        logger.info(f"✅ Zucpay - Status atualizado para cancelled: {payment_id}")
        
        notify_admin_payment_cancelled(payment_id, user_id, payment, 'Zucpay')
        return {'success': True}
    except Exception as e:
        logger.error(f"❌ Zucpay - Erro cancelled: {e}")
        return {'success': False, 'error': str(e)}

def handle_zucpay_refunded(payment_id, status, data, users_data, user_id, payment, amount):
    """Pagamento estornado Zucpay - remover saldo"""
    try:
        valor_pagamento = float(payment.get('valor', amount or 0))
        
        for user_data in users_data.get('users', []):
            if user_data['id'] == user_id:
                saldo_atual = user_data.get('saldo', 0)
                novo_saldo = max(0, saldo_atual - valor_pagamento)
                user_data['saldo'] = novo_saldo
                
                for p in user_data.get('pagamentos', []):
                    if p.get('id_pagamento') == payment_id:
                        p['status'] = 'refunded'
                        p['updated_at'] = datetime.now().isoformat()
                        break
                
                logger.info(f"✅ Zucpay - Saldo removido: R${saldo_atual:.2f} -> R${novo_saldo:.2f}")
                break
        
        save_users(users_data)
        notify_admin_payment_refunded(payment_id, user_id, payment, 'Zucpay')
        return {'success': True}
    except Exception as e:
        logger.error(f"❌ Zucpay - Erro refunded: {e}")
        return {'success': False, 'error': str(e)}

def handle_zucpay_failed(payment_id, status, data, users_data, user_id, payment):
    """Pagamento falhou Zucpay"""
    try:
        for user_data in users_data.get('users', []):
            if user_data['id'] == user_id:
                for p in user_data.get('pagamentos', []):
                    if p.get('id_pagamento') == payment_id:
                        p['status'] = 'failed'
                        p['updated_at'] = datetime.now().isoformat()
                        break
                break
        
        save_users(users_data)
        logger.info(f"✅ Zucpay - Status atualizado para failed: {payment_id}")
        
        notify_admin_payment_failed(payment_id, user_id, payment, 'Zucpay')
        return {'success': True}
    except Exception as e:
        logger.error(f"❌ Zucpay - Erro failed: {e}")
        return {'success': False, 'error': str(e)}

# ==================== ENDPOINTS DE DEBUG ZUCPAY ====================

@app.route('/debug/zucpay', methods=['POST', 'GET'])
def debug_zucpay():
    """Endpoint para debug - mostra exatamente o que chega do Zucpay"""
    if request.method == 'GET':
        return '''
        <h2>Debug Zucpay</h2>
        <p>Envie um POST para este endpoint com os dados do webhook</p>
        <form method="post">
            <textarea name="data" rows="10" cols="50"></textarea><br>
            <input type="submit" value="Enviar">
        </form>
        '''
    
    # Log detalhado de tudo que chegou
    logger.info("=" * 50)
    logger.info("🔍 DEBUG ZUCPAY - REQUISIÇÃO RECEBIDA")
    logger.info(f"IP: {request.remote_addr}")
    logger.info(f"Method: {request.method}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Content-Type: {request.content_type}")
    
    # Tentar diferentes formas de obter os dados
    data = {}
    
    # Tentar como JSON primeiro
    if request.is_json:
        data = request.get_json()
        logger.info("Dados como JSON:")
    else:
        # Tentar como form data
        data = request.form.to_dict()
        logger.info("Dados como Form:")
        
        # Se não tiver dados no form, tenta raw data
        if not data:
            raw_data = request.get_data(as_text=True)
            logger.info(f"Dados brutos: {raw_data}")
            try:
                data = json.loads(raw_data)
                logger.info("Conseguiu parsear raw data como JSON")
            except:
                data = {'raw': raw_data}
    
    logger.info(json.dumps(data, indent=2, ensure_ascii=False))
    logger.info("=" * 50)
    
    return jsonify({
        "received": True,
        "method": request.method,
        "headers": dict(request.headers),
        "content_type": request.content_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    })

# ==================== FUNÇÕES DE NOTIFICAÇÃO COMPARTILHADAS ====================

def notify_admin_payment_created(payment_id, user_id, payment, provider):
    """Notifica admin sobre pagamento criado"""
    try:
        creds = load_credenciais()
        admin_id = creds.get('id_dono')
        if not admin_id:
            return
        
        valor = payment.get('valor', 0)
        
        message = (
            f"🆕 **Nova Recarga {provider} Criada!**\n\n"
            f"👤 **Usuário:** {user_id}\n"
            f"💰 **Valor:** R${float(valor):.2f}\n"
            f"🆔 **Pagamento:** {payment_id}\n"
            f"📅 **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"⏳ **Status:** Aguardando pagamento"
        )
        
        send_telegram_message(admin_id, message)
    except Exception as e:
        logger.error(f"❌ Erro ao notificar admin: {e}")

def notify_admin_payment_approved(payment_id, user_id, payment, valor_pagamento, saldo_adicional, provider, data):
    """Notifica admin sobre pagamento aprovado"""
    try:
        creds = load_credenciais()
        admin_id = creds.get('id_dono')
        if not admin_id:
            return
        
        message = (
            f"🎉 **Recarga {provider} Aprovada!**\n\n"
            f"👤 **Usuário:** {user_id}\n"
            f"💰 **Valor Pago:** R${float(valor_pagamento):.2f}\n"
            f"💎 **Saldo Adicionado:** R${float(saldo_adicional):.2f}\n"
            f"🆔 **Pagamento:** {payment_id}\n"
            f"📅 **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"✅ **Status:** Aprovado"
        )
        
        send_telegram_message(admin_id, message)
    except Exception as e:
        logger.error(f"❌ Erro ao notificar admin: {e}")

def notify_admin_payment_cancelled(payment_id, user_id, payment, provider):
    """Notifica admin sobre pagamento cancelado"""
    try:
        creds = load_credenciais()
        admin_id = creds.get('id_dono')
        if not admin_id:
            return
        
        valor = payment.get('valor', 0)
        
        message = (
            f"❌ **Recarga {provider} Cancelada!**\n\n"
            f"👤 **Usuário:** {user_id}\n"
            f"💰 **Valor:** R${float(valor):.2f}\n"
            f"🆔 **Pagamento:** {payment_id}\n"
            f"📅 **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"🚫 **Status:** Cancelado"
        )
        
        send_telegram_message(admin_id, message)
    except Exception as e:
        logger.error(f"❌ Erro ao notificar admin: {e}")

def notify_admin_payment_refunded(payment_id, user_id, payment, provider):
    """Notifica admin sobre pagamento estornado"""
    try:
        creds = load_credenciais()
        admin_id = creds.get('id_dono')
        if not admin_id:
            return
        
        valor = payment.get('valor', 0)
        
        message = (
            f"🔄 **Recarga {provider} Estornada!**\n\n"
            f"👤 **Usuário:** {user_id}\n"
            f"💰 **Valor:** R${float(valor):.2f}\n"
            f"🆔 **Pagamento:** {payment_id}\n"
            f"📅 **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"🔄 **Status:** Estornado"
        )
        
        send_telegram_message(admin_id, message)
    except Exception as e:
        logger.error(f"❌ Erro ao notificar admin: {e}")

def notify_admin_payment_failed(payment_id, user_id, payment, provider):
    """Notifica admin sobre pagamento falhou"""
    try:
        creds = load_credenciais()
        admin_id = creds.get('id_dono')
        if not admin_id:
            return
        
        valor = payment.get('valor', 0)
        
        message = (
            f"❌ **Recarga {provider} Falhou!**\n\n"
            f"👤 **Usuário:** {user_id}\n"
            f"💰 **Valor:** R${float(valor):.2f}\n"
            f"🆔 **Pagamento:** {payment_id}\n"
            f"📅 **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"❌ **Status:** Falhou"
        )
        
        send_telegram_message(admin_id, message)
    except Exception as e:
        logger.error(f"❌ Erro ao notificar admin: {e}")

def notify_user_payment_approved(user_id, valor_pagamento, saldo_adicional, novo_saldo):
    """Notifica usuário sobre recarga aprovada"""
    try:
        message = (
            f"🎉 **Recarga Aprovada!**\n\n"
            f"💰 **Valor Pago:** R${float(valor_pagamento):.2f}\n"
            f"💎 **Saldo Adicionado:** R${float(saldo_adicional):.2f}\n"
            f"💳 **Saldo Atual:** R${float(novo_saldo):.2f}\n\n"
            f"✅ Seu saldo foi atualizado com sucesso!"
        )
        
        send_telegram_message(user_id, message)
    except Exception as e:
        logger.error(f"❌ Erro ao notificar usuário: {e}")

def delete_qr_code_messages(user_id, payment_id):
    """Deleta mensagens do QR code quando pagamento é aprovado"""
    try:
        users_data = load_users()
        
        user_found = None
        for user_data in users_data.get('users', []):
            if user_data['id'] == user_id:
                user_found = user_data
                break
        
        if not user_found:
            logger.warning(f"⚠️ Usuário {user_id} não encontrado")
            return
        
        qr_messages = user_found.get('qr_messages', [])
        if not qr_messages:
            return
        
        deleted_count = 0
        for message_id in qr_messages:
            if delete_telegram_message(user_id, message_id):
                deleted_count += 1
        
        user_found['qr_messages'] = []
        save_users(users_data)
        
        logger.info(f"✅ {deleted_count} mensagens QR deletadas para usuário {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao deletar mensagens QR: {e}")

# ==================== ENDPOINTS AUXILIARES ====================

@app.route('/webhook/zucpay-sms/health', methods=['GET'])
def health_check():
    """Verifica se o webhook está funcionando"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'processed_payments': len(processed_events)
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/webhook/zucpay-sms/clear-cache', methods=['POST'])
def clear_cache():
    """Limpa o cache de pagamentos processados"""
    try:
        with transaction_lock:
            count = len(processed_events)
            processed_events.clear()
            logger.info(f"🧹 Cache limpo: {count} pagamentos removidos")
            return jsonify({
                'success': True,
                'cleared_payments': count,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"❌ Erro ao limpar cache: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/zucpay-sms/status', methods=['GET'])
def webhook_status():
    """Mostra status detalhado do webhook"""
    return jsonify({
        'status': 'running',
        'processed_payments_count': len(processed_events),
        'processed_payments': list(processed_events.keys())[-10:] if processed_events else [],
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("🚀 Iniciando Webhook Zucpay na porta 8080")
    logger.info("📌 Zucpay: /webhook/zucpay-sms")
    logger.info("📌 Debug Zucpay: /debug/zucpay")
    app.run(host='0.0.0.0', port=8080, debug=False)
