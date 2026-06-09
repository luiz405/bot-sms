def mostrar_provedores_para_precos(message, servico, pais):
    """Exibe botões para o usuário escolher o provedor antes de mostrar os preços/pools."""
    texto = "<b>Escolha o provedor para ver todos os preços:</b>"
    buttons = []
    clients = api.sms_clients_all()
    for i, client in enumerate(clients, 1):
        provider_name = client.provider.lower()
        if provider_name == "herosms":
            label = "Provedor 1"
        elif provider_name == "grizzly":
            label = "Provedor 2"
        else:
            label = f"Provedor {i}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"listar_precos_provedor {servico} {pais} {client.provider}")])
    buttons.append([InlineKeyboardButton("🔙 VOLTAR", callback_data=f"exibir_servico {servico}")])
    markup = InlineKeyboardMarkup(buttons)
    try:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=texto,
            parse_mode="HTML",
            reply_markup=markup
        )
    except Exception as e:
        if "message is not modified" in str(e).lower():
            pass
        else:
            print(f"Erro ao editar mensagem: {e}")

def safe_edit_message(chat_id, message_id, text, parse_mode='HTML', reply_markup=None):
    """Edita mensagem com segurança, lidando com erros comuns"""
    try:
        if not text or text.strip() == "":
            print(f"⚠️ [SAFE_EDIT] Tentativa de editar mensagem sem texto: {message_id}")
            text = "⚠️ Mensagem atualizada (sem conteúdo de texto)"
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
        return True
    except Exception as e:
        error_str = str(e)
        if "message to edit not found" in error_str.lower():
            print(f"ℹ️ [SAFE_EDIT] Mensagem {message_id} não encontrada para editar")
            try:
                bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
                return True
            except:
                return False
        elif "message is not modified" in error_str.lower():
            print(f"ℹ️ [SAFE_EDIT] Mensagem {message_id} não foi modificada")
            return True
        else:
            print(f"⚠️ [SAFE_EDIT] Erro ao editar mensagem {message_id}: {error_str}")
            return False

def safe_answer_callback(call, text, show_alert=True):
    """Responde callback query com segurança"""
    try:
        bot.answer_callback_query(call.id, text, show_alert=show_alert)
        return True
    except Exception as e:
        print(f"⚠️ [CALLBACK] Não foi possível responder: {e}")
        if hasattr(call, 'message') and call.message:
            try:
                bot.send_message(call.message.chat.id, text, parse_mode='HTML')
            except:
                pass
        return False

# ==================== LOADING & DEPENDENCY CHECK ====================
def instalar_dependencia(pacote):
    """Instala uma dependência automaticamente"""
    try:
        print(f"   📦 Instalando {pacote}...", end='', flush=True)
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pacote, "--quiet"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"\r   ✅ {pacote} - INSTALADO COM SUCESSO")
        return True
    except Exception as e:
        print(f"\r   ❌ {pacote} - ERRO NA INSTALAÇÃO: {e}")
        return False

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas e instala as faltando"""
    dependencias = {
        'telebot': 'pyTelegramBotAPI',
        'Levenshtein': 'Levenshtein',
        'pytz': 'pytz',
        'requests': 'requests',
        'flask': 'flask',
        'httpx': 'httpx',
        'qrcode': 'qrcode',
        'PIL': 'pillow',
        'apscheduler': 'APScheduler',
        'matplotlib': 'matplotlib'
    }
    
    print("\n🔍 Verificando dependências...\n")
    
    faltando = []
    for modulo, pacote in dependencias.items():
        try:
            print(f"   ⏳ Verificando {pacote}...", end='\r')
            time.sleep(0.05)
            
            spec = importlib.util.find_spec(modulo)
            if spec is None:
                print(f"   ⚠️  {pacote} - NÃO INSTALADO")
                faltando.append((modulo, pacote))
            else:
                print(f"   ✅ {pacote} - OK          ")
        except Exception as e:
            print(f"   ⚠️  {pacote} - NÃO ENCONTRADO")
            faltando.append((modulo, pacote))
    
    if faltando:
        print(f"\n📦 Instalando {len(faltando)} dependência(s) automaticamente...\n")
        
        falhas = []
        for modulo, pacote in faltando:
            if not instalar_dependencia(pacote):
                falhas.append(pacote)
        
        if falhas:
            print(f"\n❌ ERRO: Não foi possível instalar: {', '.join(falhas)}")
            print(f"💡 Tente manualmente: pip install {' '.join(falhas)}")
            return False
        
        print("\n✅ Todas as dependências foram instaladas com sucesso!")
    else:
        print("\n✅ Todas as dependências já estão instaladas!")
    
    return True

def mostrar_loading():
    """Mostra animação de loading"""
    frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    mensagens = [
        "Inicializando sistema",
        "Carregando módulos",
        "Preparando ambiente",
        "Configurando bot"
    ]
    
    for msg in mensagens:
        for _ in range(10):
            for frame in frames:
                print(f"\r   {frame} {msg}...", end='', flush=True)
                time.sleep(0.05)
        print(f"\r   ✅ {msg}... OK!     ")

import sys
import importlib.util
import subprocess
import json
import string
import telebot
from telebot import types
import Levenshtein
import time
import datetime
import shutil
import os
import threading
import random
import zipfile
import requests
import api
from api import gn
from os import system
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    ForceReply,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from api import (
    CredentialsChange, 
    InfoUser, 
    MudancaHistorico, 
    AfiliadosInfo,
    CriarPix,
    LogManager,
    Log,
    CooldownCancelamento,
    LimiteGeracao
)
import threading
import functools
from contextlib import contextmanager

# ==================== FUNÇÃO PARA IDENTIFICAR PROVEDOR ====================
def identificar_provedor_ativacao(id_ativacao, user_id=None):
    """
    Identifica em qual provedor uma ativação foi gerada
    Retorna: nome_do_provedor ou None
    """
    try:
        # Cache para evitar leituras repetidas do JSON
        if not hasattr(identificar_provedor_ativacao, 'cache'):
            identificar_provedor_ativacao.cache = {}
            identificar_provedor_ativacao.cache_timeout = 300  # 5 minutos
        
        cache_key = f"{id_ativacao}_{user_id}"
        now = time.time()
        
        if cache_key in identificar_provedor_ativacao.cache:
            cached_data, cached_time = identificar_provedor_ativacao.cache[cache_key]
            if now - cached_time < identificar_provedor_ativacao.cache_timeout:
                print(f"🔍 [PROVEDOR CACHE] {id_ativacao} -> {cached_data}")
                return cached_data
        
        with open('database/users.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        provedor_encontrado = None
        
        # Se temos user_id, buscar direto naquele usuário
        if user_id:
            for user in data["users"]:
                if int(user["id"]) == int(user_id):
                    for compra in user.get("compras", []):
                        if str(compra.get("id_ativacao", "")) == str(id_ativacao):
                            provedor_encontrado = compra.get("provedor", "herosms")
                            print(f"🔍 [PROVEDOR] Ativação {id_ativacao} -> Provedor: {provedor_encontrado} (via user_id)")
                            identificar_provedor_ativacao.cache[cache_key] = (provedor_encontrado, now)
                            return provedor_encontrado
                    break
        
        # Busca global (mais lenta)
        for user in data["users"]:
            for compra in user.get("compras", []):
                if str(compra.get("id_ativacao", "")) == str(id_ativacao):
                    provedor_encontrado = compra.get("provedor", "herosms")
                    print(f"🔍 [PROVEDOR] Ativação {id_ativacao} -> Provedor: {provedor_encontrado} (usuário {user['id']})")
                    identificar_provedor_ativacao.cache[cache_key] = (provedor_encontrado, now)
                    return provedor_encontrado
        
        print(f"⚠️ [PROVEDOR] Ativação {id_ativacao} não encontrada no banco de dados")
        return None
    except Exception as e:
        print(f"❌ [PROVEDOR] Erro ao identificar provedor: {e}")
        return None
        
def verificar_status_em_todos_provedores(id_ativacao):
    """
    Verifica o status de uma ativação em todos os provedores
    Retorna: (status, provedor) ou (None, None)
    """
    provedores = ["herosms", "grizzly"]
    for provedor in provedores:
        try:
            status = api.InfoApi.pegar_status_numero(id_ativacao, provedor=provedor)
            if status is not False and status is not None:
                print(f"✅ Status encontrado no provedor {provedor}: {status}")
                return status, provedor
        except Exception as e:
            print(f"⚠️ Erro ao verificar {provedor}: {e}")
            continue
    return None, None

# ==================== LOCKS PARA OPERAÇÕES DE SALDO ====================
# Locks por usuário para evitar race conditions
saldo_locks = {}
saldo_locks_lock = threading.Lock()

def get_user_lock(user_id):
    """Obtém ou cria um lock para um usuário específico"""
    with saldo_locks_lock:
        if user_id not in saldo_locks:
            saldo_locks[user_id] = threading.Lock()
        return saldo_locks[user_id]

@contextmanager
def saldo_operation_lock(user_id):
    """Context manager para operações de saldo seguras"""
    lock = get_user_lock(user_id)
    acquired = lock.acquire(timeout=10)
    try:
        if not acquired:
            raise Exception(f"Não foi possível adquirir lock para usuário {user_id}")
        yield
    finally:
        if acquired:
            lock.release()

# ==================== FUNÇÕES SEGURAS DE SALDO ====================
def adicionar_saldo_seguro(user_id, valor):
    """Adiciona saldo ao usuário de forma segura (thread-safe)"""
    with saldo_operation_lock(user_id):
        return api.InfoUser.add_saldo(user_id, valor)

def remover_saldo_seguro(user_id, valor):
    """Remove saldo do usuário de forma segura (thread-safe)"""
    with saldo_operation_lock(user_id):
        return api.InfoUser.tirar_saldo(user_id, valor)

def processar_reembolso_seguro(user_id, id_ativacao, valor, provedor_usado=None):
    """
    Processa reembolso de forma segura, garantindo que não haja duplicidade
    Retorna: (sucesso, mensagem)
    """
    with saldo_operation_lock(user_id):
        if api.InfoUser.verificar_reembolso_duplicado(user_id, id_ativacao):
            print(f"⚠️ [REEMBOLSO DUPLICADO] Ativação {id_ativacao} já foi processada")
            return False, "Já reembolsado"
        
        try:
            # PASSAR O PROVEDOR CORRETO!
            resultado = api.InfoApi.mudar_status_numero(id_ativacao, '8', provedor_usado)
            
            print(f"📤 [REEMBOLSO] Resultado da API ({provedor_usado}): {resultado}")
            
            if resultado == 'ACCESS_CANCEL' or (isinstance(resultado, str) and 'ACCESS_CANCEL' in resultado):
                api.InfoUser.add_saldo(user_id, float(valor))
                api.InfoUser.marcar_como_reembolsado(user_id, id_ativacao)
                api.MudancaHistorico.add_reembolso(user_id, id_ativacao, valor)
                print(f"✅ [REEMBOLSO] ID:{id_ativacao} | User:{user_id} | Valor:{valor} | Provedor:{provedor_usado}")
                return True, "Reembolso processado com sucesso"
            else:
                print(f"❌ [REEMBOLSO] Falha ao cancelar no provedor {provedor_usado}: {resultado}")
                return False, f"Falha ao cancelar na API: {resultado}"
        except Exception as e:
            print(f"❌ [REEMBOLSO] Erro: {e}")
            return False, f"Erro: {str(e)}"

# ==================== STARTUP SEQUENCE ====================
print("\n" + "="*60)
print("INICIANDO O BOT SMS :)")
print("="*60 + "\n")

# 1. Exibir ASCII art
try:
    with open('textos/acsi.txt', 'r', encoding='utf-8') as f:
        ascii_lines = f.read().splitlines()
    
    if ascii_lines:
        for line in ascii_lines:
            print(line)
            time.sleep(0.05)
        print("\n")
except Exception as e:
    print(f"⚠️ Não foi possível carregar ASCII art: {e}\n")

print("="*60)

# 2. Loading inicial
mostrar_loading()

# 3. Verificar dependências
if not verificar_dependencias():
    print("\n❌ Falha na verificação de dependências. Encerrando...")
    sys.exit(1)

print("\n" + "="*60)
print("✅ SISTEMA PRONTO - INICIANDO BOT...")
print("="*60 + "\n")

# ==================== LOG CONTROL ====================
MOSTRAR_LOGS = True

def carregar_config_logs():
    """Carrega configuração de logs do arquivo de credenciais"""
    global MOSTRAR_LOGS
    try:
        with open('settings/credenciais.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        MOSTRAR_LOGS = config.get('mostrar_logs_terminal', True)
    except:
        MOSTRAR_LOGS = True

def log_print(*args, **kwargs):
    """Print condicional baseado na configuração"""
    if MOSTRAR_LOGS:
        _original_print(*args, **kwargs)

carregar_config_logs()

_original_print = print
if not MOSTRAR_LOGS:
    import builtins
    builtins.print = log_print

bot = telebot.TeleBot(api.CredentialsChange.token_bot())

# ==================== GLOBAL VARIABLES ====================
cancel_data = {}
bloqueio_mensagens_cache = {}
BLOQUEIO_CACHE_TEMPO = 30

# ==================== HELPER FUNCTIONS ====================
def safe_send_message(chat_id, text, parse_mode='HTML', reply_markup=None, reply_to_message_id=None):
    """Envia mensagem com reply_to_message_id seguro"""
    try:
        return bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id
        )
    except Exception as e:
        if "message to be replied not found" in str(e).lower():
            return bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        else:
            raise e

def safe_send_photo(chat_id, photo, caption=None, parse_mode='HTML', reply_markup=None, reply_to_message_id=None):
    """Envia foto com reply_to_message_id seguro"""
    try:
        return bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id
        )
    except Exception as e:
        if "message to be replied not found" in str(e).lower():
            return bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        else:
            raise e

# ==================== PRICING CACHE UPDATER ====================
pricing_scheduler = BackgroundScheduler()

def atualizar_cache_precos():
    """Atualiza o cache de preços"""
    import concurrent.futures
    from threading import Lock
    import requests
    import time
    
    try:
        log_print("🚀 [CACHE UPDATER] Iniciando atualização...")
        start_time = time.time()
        
        with open('settings/traducoes_servicos.json', 'r', encoding='utf-8') as f:
            traducoes_data = json.load(f)
        servicos_disponiveis = list(traducoes_data.get("traducoes", {}).keys())
        
        servicos_atualizados = 0
        servicos_processados = 0
        total_servicos = len(servicos_disponiveis)
        counter_lock = Lock()
        
        session = requests.Session()
        session.headers.update({
            'Connection': 'keep-alive',
            'Keep-Alive': 'timeout=30, max=100'
        })
        
        def processar_servico_otimizado(servico_id):
            nonlocal servicos_atualizados, servicos_processados
            try:
                precos_todos_paises = api.sms.getPrices(str(servico_id), "")
                
                if isinstance(precos_todos_paises, dict) and "error" not in precos_todos_paises:
                    paises_processados = {}
                    ofertas = []
                    
                    for pais_id, servicos_data in precos_todos_paises.items():
                        if isinstance(servicos_data, dict) and str(servico_id) in servicos_data:
                            info = servicos_data[str(servico_id)]
                            if isinstance(info, dict):
                                count = int(info.get("count", 0))
                                cost = float(info.get("cost", 0))
                                
                                if count > 0 and cost > 0:
                                    ofertas.append({"pais": pais_id, "valor": cost})
                    
                    if ofertas:
                        lista_ordenada = sorted(ofertas, key=lambda x: x["valor"])[:20]
                        
                        for oferta in lista_ordenada:
                            try:
                                pais_id = oferta["pais"]
                                pais_nome = api.InfoApi.pegar_pais(pais_id)
                                valor = oferta["valor"]
                                
                                if str(pais_id) == '73':
                                    try:
                                        with open('settings/substituir_valor.json', 'r') as f:
                                            data = json.load(f)
                                        for servico_mod in data["servicos"]:
                                            if str(servico_id) == servico_mod["id"]:
                                                valor = float(servico_mod["valor"])
                                                break
                                    except Exception:
                                        pass
                                
                                paises_processados[pais_id] = {
                                    "nome": pais_nome,
                                    "valor": float(valor)
                                }
                            except Exception as e:
                                continue
                        
                        if paises_processados:
                            nome_servico = traducoes_data["traducoes"].get(servico_id, f"Serviço {servico_id}")
                            
                            cache_data = {
                                "timestamp": time.time(),
                                "dados": {
                                    "nome_servico": nome_servico,
                                    "paises": paises_processados
                                }
                            }
                            
                            os.makedirs('cache_comparativos', exist_ok=True)
                            cache_file = f'cache_comparativos/{servico_id}.json'
                            
                            with open(cache_file, 'w', encoding='utf-8') as f:
                                json.dump(cache_data, f, indent=2, ensure_ascii=False)
                            
                            with counter_lock:
                                servicos_atualizados += 1
                            
                            if servicos_atualizados % 10 == 0:
                                log_print(f"✅ [CACHE] {servico_id} ({nome_servico}) - {len(paises_processados)} países | Total: {servicos_atualizados}")
                            return True
                        else:
                            log_print(f"⚠️ [CACHE] {servico_id} - Nenhum país com dados válidos")
                else:
                    log_print(f"⚠️ [CACHE] {servico_id} - API retornou erro ou dados inválidos")
                
            except Exception as e:
                log_print(f"❌ [CACHE] Erro {servico_id}: {e}")
            finally:
                with counter_lock:
                    servicos_processados += 1
                    if servicos_processados % 50 == 0:
                        elapsed = time.time() - start_time
                        progress = (servicos_processados / total_servicos) * 100
                        rate = servicos_processados / elapsed if elapsed > 0 else 0
                        eta_seconds = (total_servicos - servicos_processados) / rate if rate > 0 else 0
                        eta_minutes = eta_seconds / 60
                        log_print(f"📊 [PROGRESSO] {servicos_processados}/{total_servicos} ({progress:.1f}%) | {rate:.1f}/s | Cached: {servicos_atualizados} | ETA: {eta_minutes:.1f}min")
            
            return False
        
        log_print(f"🚀 [CACHE] Processando {total_servicos} serviços em lotes de 15 com intervalos...")
        
        batch_size = 15
        max_workers = 5
        
        for i in range(0, total_servicos, batch_size):
            batch = servicos_disponiveis[i:i + batch_size]
            
            if (i//batch_size + 1) % 5 == 0 or i == 0:
                log_print(f"📦 [LOTE] Processando lote {i//batch_size + 1}/{(total_servicos + batch_size - 1)//batch_size} ({len(batch)} serviços)")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(processar_servico_otimizado, servico_id) for servico_id in batch]
                concurrent.futures.wait(futures)
            
            if i + batch_size < total_servicos:
                log_print(f"⏱️ [RATE LIMIT] Aguardando 5s antes do próximo lote...")
                time.sleep(5)
        
        session.close()
        
        elapsed_time = time.time() - start_time
        rate = servicos_processados / elapsed_time if elapsed_time > 0 else 0
        
        log_print(f"🎉 [CACHE UPDATER] CONCLUÍDO!")
        log_print(f"📊 {servicos_atualizados}/{total_servicos} serviços cached em {elapsed_time:.1f}s ({rate:.1f}/s)")
        
    except Exception as e:
        log_print(f"❌ [CACHE UPDATER] Erro crítico: {e}")

def iniciar_atualizador_precos():
    """Inicia o sistema de atualização automática de preços"""
    try:
        if not pricing_scheduler.running:
            pricing_scheduler.start()
            log_print("✅ [CACHE UPDATER] Scheduler de preços iniciado")
        
        try:
            pricing_scheduler.remove_job('update_pricing_cache')
        except:
            pass
        
        pricing_scheduler.add_job(
            func=atualizar_cache_precos,
            trigger='interval',
            minutes=60,
            id='update_pricing_cache',
            replace_existing=True
        )
        
        log_print("📅 [CACHE UPDATER] Agendamento configurado para atualizar a cada 60 minutos")
        
        threading.Thread(target=atualizar_cache_precos, daemon=True).start()
        
    except Exception as e:
        log_print(f"❌ [CACHE UPDATER] Erro ao iniciar atualizador de preços: {e}")

threading.Thread(target=iniciar_atualizador_precos, daemon=True).start()

def enviar_log_multiplos_destinos(texto, tipo_log, parse_mode='HTML', reply_markup=None):
    """Envia logs para múltiplos canais configurados com tratamento seguro de formatação"""
    try:
        if isinstance(texto, str):
            texto = texto.replace('{', '{{').replace('}', '}}')
            
            import re
            def replace_float(match):
                try:
                    valor = float(match.group(1))
                    return f"R${valor:.2f}"
                except:
                    return match.group(0)
            
            texto = re.sub(r'R\$(\d+\.?\d*)', replace_float, texto)
        
        canais = api.LogManager.listar_canais(tipo_log)
        
        if not canais:
            log_print(f"[LOG {tipo_log}] ⚠️ Nenhum canal configurado")
            return 0, 0
        
        sucessos = 0
        falhas = 0
        
        for canal in canais:
            if not canal or canal in ["SEUID", "ID", ""]:
                log_print(f"[LOG {tipo_log}] ⚠️ Canal inválido ignorado: {canal}")
                continue
            
            try:
                valido, tipo, _ = api.Log.validar_destino(canal)
                if valido:
                    log_print(f"[LOG {tipo_log}] Enviando para {canal} ({tipo})...")
                    bot.send_message(
                        chat_id=canal,
                        text=texto,
                        parse_mode=parse_mode,
                        reply_markup=reply_markup
                    )
                    log_print(f"[LOG {tipo_log}] ✅ Enviado com sucesso para {canal}")
                    sucessos += 1
                else:
                    log_print(f"[LOG {tipo_log}] ⚠️ Canal inválido: {canal} - {tipo}")
                    falhas += 1
            except Exception as e:
                log_print(f"[LOG {tipo_log}] ❌ Erro ao enviar para {canal}: {e}")
                falhas += 1
        
        log_print(f"[LOG {tipo_log}] Resumo: {sucessos} enviados, {falhas} falhas")
        return sucessos, falhas
        
    except Exception as e:
        log_print(f"[LOG {tipo_log}] ❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0

try:
    bot.send_message(chat_id=api.CredentialsChange.id_dono(), text='[BOT] <b>SEU BOT FOI REINICIADO!</b>', parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('PAINEL ADM', callback_data='voltar_paineladm')]]))
    log_print("Notificacao de reinicializacao enviada para o administrador")
except Exception as e:
    log_print(f"Erro ao enviar notificacao de reinicializacao: {e}")
    log_print("Certifique-se de que o ID do administrador esta correto e que voce iniciou uma conversa com o bot")

#Painel adm
@bot.message_handler(commands=['admin'])
def painel_admin(message, opcao:str|None=None):
    if opcao == None:
        opcao = 'total'
    if api.Admin.verificar_admin(message.chat.id) == True or int(message.chat.id) == int(api.CredentialsChange.id_dono()):
        if opcao == 'total':
            tipo = 'TOTAL'
            mudar = 'today'
            resp = api.MetricasVendas.total()
            receita, gasto = resp["receita"], resp["gasto"]
        if opcao == 'today':
            tipo = 'HOJE'
            mudar = '7'
            resp = api.MetricasVendas.hoje()
            receita, gasto = resp["receita"], resp["gasto"]
        if opcao == '7':
            tipo = '7 DIAS'
            mudar = '30'
            resp = api.MetricasVendas.sete()
            receita, gasto = resp["receita"], resp["gasto"]
        if opcao == '30':
            tipo = '30 DIAS'
            mudar = 'total'
            resp = api.MetricasVendas.trinta()
            receita, gasto = resp["receita"], resp["gasto"]
        
        total_usuarios = api.Admin.total_users()
        b = InlineKeyboardButton(f'RECEITA: {tipo}', callback_data=f'mudar_receita {mudar}')
        bt = InlineKeyboardButton('CONFIGURACOES', callback_data='admin_configuracoes')
        bt2 = InlineKeyboardButton('MENU DE EDICOES', callback_data='menu_edicoes')
        if api.CredentialsChange.PlataformaPix.status_zucpay():
            bt3 = InlineKeyboardButton('MONITORAMENTO CONTA ZUCPAY', callback_data='monitoramentozucpayconta')
        else:
            bt3 = None
        bt4 = InlineKeyboardButton('GIFT CARD', callback_data='gift_card')
        bt5 = InlineKeyboardButton('BAIXAR BACKUP DO BOT', callback_data='baixar_backup_bot')
        bt6 = InlineKeyboardButton('👨‍💻 ZUCPAY SITE', url='https://zucpay.com')
        
        versao_bot = api.CredentialsChange.obter_versao_bot()
        texto = f'[ADMIN] <b>PAINEL DE GERENCIAMENTO @{api.CredentialsChange.user_bot()}</b>\nEstatisticas:\nUsuarios: {total_usuarios}\nReceita ({tipo}): R${receita}\nGasto na api ({tipo}): R${gasto}\nVersao: {versao_bot}\n\nUse os botoes abaixo para me configurar\n\n<b><a href="https://zucpay.com">ZUCPAY</a> © <code>zucpay</code></b>'
        botoes = [[b], [bt], [bt2]]
        if bt3:
            botoes.append([bt3])
        botoes.extend([[bt4], [bt5], [bt6]])
        markup = InlineKeyboardMarkup(botoes)
        if message.text != '/admin':
            safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)
        else:
            safe_send_message(message.chat.id, texto, parse_mode='HTML', reply_markup=markup, reply_to_message_id=message.message_id)
    else:
        bot.reply_to(message, "Você não é um adm!")
        return

@bot.message_handler(commands=['atualizar_cache'])
def handle_atualizar_cache(message):
    if api.Admin.verificar_admin(message.chat.id) == True or int(message.chat.id) == int(api.CredentialsChange.id_dono()):
        bot.reply_to(message, "🔄 Iniciando atualização manual do cache de preços...")
        def executar_atualizacao():
            try:
                atualizar_cache_precos()
                bot.send_message(message.chat.id, "✅ Cache de preços atualizado com sucesso!")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Erro ao atualizar cache: {str(e)}")
        threading.Thread(target=executar_atualizacao, daemon=True).start()
    else:
        bot.reply_to(message, "❌ Você não tem permissão para usar este comando!")

@bot.message_handler(commands=['status_cache'])
def handle_status_cache(message):
    if api.Admin.verificar_admin(message.chat.id) == True or int(message.chat.id) == int(api.CredentialsChange.id_dono()):
        try:
            cache_files = [f for f in os.listdir('cache_comparativos') if f.endswith('.json')]
            total_arquivos = len(cache_files)
            
            arquivos_recentes = []
            arquivos_antigos = []
            tempo_atual = time.time()
            
            for arquivo in cache_files[:10]:
                try:
                    with open(f'cache_comparativos/{arquivo}', 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    timestamp = data.get('timestamp', 0)
                    idade = tempo_atual - timestamp
                    
                    if idade < 600:
                        arquivos_recentes.append(arquivo)
                    else:
                        arquivos_antigos.append(arquivo)
                except:
                    continue
            
            scheduler_status = "🟢 Ativo" if pricing_scheduler.running else "🔴 Inativo"
            
            texto = f"""📊 <b>STATUS DO CACHE DE PREÇOS</b>

🗂️ <b>Arquivos de Cache:</b> {total_arquivos}
⏰ <b>Scheduler:</b> {scheduler_status}
🔄 <b>Intervalo:</b> 10 minutos

📈 <b>Arquivos Recentes:</b> {len(arquivos_recentes)}
📉 <b>Arquivos Antigos:</b> {len(arquivos_antigos)}

💡 <b>Comandos:</b>
• /atualizar_cache - Força atualização manual
• /status_cache - Mostra este status"""
            
            bot.reply_to(message, texto, parse_mode='HTML')
            
        except Exception as e:
            bot.reply_to(message, f"❌ Erro ao verificar status: {str(e)}")
    else:
        bot.reply_to(message, "❌ Você não tem permissão para usar este comando!")

@bot.message_handler(commands=['mudar_api'])
def handle_changeapi(message):
    txt = message.text
    if len(txt.split(' ')) == 2:
        api_nova = txt.split(' ')[1]
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        prov = str(data.get("sms_provider", "herosms")).strip().lower()
        if prov == "grizzly":
            data["api-sms-grizzly"] = str(api_nova).strip()
        else:
            data["api-sms-herosms"] = str(api_nova).strip()
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
        bot.reply_to(message, "Alterado com sucesso!")
    else:
        bot.reply_to(message, "Você enviou em um formato não permitido. Envie:\n\n/mudar_api TOKEN DA API AQUI")

@bot.message_handler(commands=['mudar_api_herosms'])
def handle_changeapi_herosms(message):
    txt = message.text
    if len(txt.split(' ')) == 2:
        api_nova = txt.split(' ')[1]
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["api-sms-herosms"] = str(api_nova).strip()
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
        bot.reply_to(message, "Chave do Hero-SMS alterada com sucesso!")
    else:
        bot.reply_to(message, "Formato inválido. Envie:\n\n/mudar_api_herosms TOKEN")

@bot.message_handler(commands=['mudar_api_grizzly'])
def handle_changeapi_grizzly(message):
    txt = message.text
    if len(txt.split(' ')) == 2:
        api_nova = txt.split(' ')[1]
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["api-sms-grizzly"] = str(api_nova).strip()
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
        bot.reply_to(message, "Chave do GrizzlySMS alterada com sucesso!")
    else:
        bot.reply_to(message, "Formato inválido. Envie:\n\n/mudar_api_grizzly TOKEN")

@bot.message_handler(commands=['limpar_pagamentos_duplicados'])
def limpar_pagamentos_duplicados(message):
    if api.Admin.verificar_admin(message.chat.id) == True or int(message.chat.id) == int(api.CredentialsChange.id_dono()):
        try:
            with open('database/users.json', 'r') as f:
                data = json.load(f)
            
            total_duplicados = 0
            usuarios_afetados = 0
            
            for user in data["users"]:
                pagamentos_originais = len(user.get("pagamentos", []))
                pagamentos_unicos = {}
                for pagamento in user.get("pagamentos", []):
                    id_pag = pagamento.get("id_pagamento")
                    if id_pag not in pagamentos_unicos:
                        pagamentos_unicos[id_pag] = pagamento
                
                user["pagamentos"] = list(pagamentos_unicos.values())
                
                duplicados_removidos = pagamentos_originais - len(user["pagamentos"])
                if duplicados_removidos > 0:
                    total_duplicados += duplicados_removidos
                    usuarios_afetados += 1
                    print(f"🧹 Usuário {user['id']}: {duplicados_removidos} duplicados removidos")
            
            api._save_users_json_safe(data)
            
            texto = f"✅ <b>LIMPEZA CONCLUÍDA</b>\n\n📊 <b>Resultados:</b>\n• Duplicados removidos: {total_duplicados}\n• Usuários afetados: {usuarios_afetados}\n\n💾 Banco de dados atualizado com sucesso!"
            bot.reply_to(message, texto, parse_mode='HTML')
            
        except Exception as e:
            bot.reply_to(message, f"❌ Erro ao limpar duplicados: {str(e)}")
    else:
        bot.reply_to(message, "❌ Você não tem permissão para usar este comando!")

@bot.message_handler(commands=['relatorio_mensal'])
def comando_relatorio_mensal(message):
    if api.Admin.verificar_admin(message.chat.id) == True or int(message.chat.id) == int(api.CredentialsChange.id_dono()):
        bot.reply_to(message, "📊 Gerando relatório mensal...")
        def executar():
            try:
                gerar_relatorio_mensal()
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Erro ao gerar relatório: {str(e)}")
        threading.Thread(target=executar, daemon=True).start()
    else:
        bot.reply_to(message, "❌ Você não tem permissão para usar este comando!")

@bot.message_handler(commands=['auditoria'])
def executar_auditoria_manual(message):
    if api.Admin.verificar_admin(message.chat.id) == True or int(message.chat.id) == int(api.CredentialsChange.id_dono()):
        bot.reply_to(message, "🔍 Iniciando auditoria manual do sistema...")
        def executar():
            try:
                verificar_inconsistencias()
                bot.send_message(message.chat.id, "✅ Auditoria concluída! Verifique o canal de logs de auditoria.")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Erro ao executar auditoria: {str(e)}")
        threading.Thread(target=executar, daemon=True).start()
    else:
        bot.reply_to(message, "❌ Você não tem permissão para usar este comando!")

@bot.message_handler(commands=['migrar_status_compras'])
def migrar_status_compras(message):
    if api.Admin.verificar_admin(message.chat.id) == True or int(message.chat.id) == int(api.CredentialsChange.id_dono()):
        try:
            with open('database/users.json', 'r') as f:
                data = json.load(f)
            
            total_compras_migradas = 0
            usuarios_afetados = 0
            
            for user in data["users"]:
                compras_usuario_migradas = 0
                for compra in user.get("compras", []):
                    if "status" not in compra:
                        compra["status"] = "ativa"
                        compras_usuario_migradas += 1
                        total_compras_migradas += 1
                if compras_usuario_migradas > 0:
                    usuarios_afetados += 1
                    print(f"🔄 Usuário {user['id']}: {compras_usuario_migradas} compras migradas")
            
            api._save_users_json_safe(data)
            
            texto = f"✅ <b>MIGRAÇÃO CONCLUÍDA</b>\n\n📊 <b>Resultados:</b>\n• Compras migradas: {total_compras_migradas}\n• Usuários afetados: {usuarios_afetados}\n\n💾 Banco de dados atualizado com sucesso!\n\n📝 <b>Nota:</b> Compras antigas foram marcadas como 'ativa' por padrão."
            bot.reply_to(message, texto, parse_mode='HTML')
            
        except Exception as e:
            bot.reply_to(message, f"❌ Erro ao migrar status: {str(e)}")
    else:
        bot.reply_to(message, "❌ Você não tem permissão para usar este comando!")

def gerar_backup_bot(message):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_bot_{timestamp}.zip"
        
        with zipfile.ZipFile(backup_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            items_to_backup = [
                'bot.py', 'api.py', 'credenciais.py', 'gerar_chave_evp.py',
                'gerar_cobranca.py', 'requirements.txt', 'discloud.config',
                'squarecloud.app', 'botoes/', 'database/', 'img/', 'infosms/',
                'log/', 'settings/', 'textos/', 'historico_cache/'
            ]
            for item in items_to_backup:
                if os.path.exists(item):
                    if os.path.isfile(item):
                        zipf.write(item)
                    elif os.path.isdir(item):
                        for root, dirs, files in os.walk(item):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, '.')
                                zipf.write(file_path, arcname)
        
        with open(backup_filename, 'rb') as backup_file:
            bot.send_document(
                chat_id=message.chat.id,
                document=backup_file,
                caption=f"💾 <b>BACKUP DO BOT GERADO</b>\n\n📅 Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n📁 Arquivo: {backup_filename}\n\n✅ Backup completo realizado com sucesso!",
                parse_mode='HTML'
            )
        
        os.remove(backup_filename)
        
    except Exception as e:
        bot.reply_to(message, f"Erro ao gerar backup: {str(e)}")

def admin_configuracoes(message):
    bt = InlineKeyboardButton('⚙️ CONFIGURACOES GERAIS', callback_data='configuracoes_geral')
    bt2 = InlineKeyboardButton('🕵️ CONFIGURAR ADMINS', callback_data='configurar_admins')
    bt3 = InlineKeyboardButton('👥 CONFIGURAR AFILIADOS', callback_data='configurar_afiliados')
    bt4 = InlineKeyboardButton('👤 CONFIGURAR USUARIOS', callback_data='configurar_usuarios')
    bt5 = InlineKeyboardButton('💠 CONFIGURAR PIX', callback_data='configurar_pix')
    bt6 = InlineKeyboardButton('🖥 CONFIGURAR VALORES', callback_data='configurar_valores')
    bt_sms = InlineKeyboardButton('📲 PROVEDOR SMS', callback_data='configurar_sms_provider')
    bt7 = InlineKeyboardButton('💰 AVISO DE SALDO (api)', callback_data='configurar_aviso_saldo_api')
    bt8 = InlineKeyboardButton('🔗 VERIFICAÇÃO DE CANAL', callback_data='configurar_verificacao_canal')
    bt9 = InlineKeyboardButton('📊 ESTATISTICAS DO BOT', callback_data='estatisticas_bot')
    bt10 = InlineKeyboardButton('⭐ SERVIÇOS EM DESTAQUE', callback_data='gerenciar_servicos_destaque')
    bt_cooldown = InlineKeyboardButton('⏱️ CONFIGURAR COOLDOWN', callback_data='configurar_cooldown_cancelamento')
    bt_logs = InlineKeyboardButton('📋 GERENCIAR CANAIS DE LOG', callback_data='gerenciar_canais_log')
    bt_broadcast = InlineKeyboardButton('📢 GERENCIAR GRUPOS DE DIVULGAÇÃO', callback_data='gerenciar_grupos_divulgacao')
    bt11 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_paineladm')
    markup = InlineKeyboardMarkup([[bt], [bt2], [bt3], [bt4], [bt5], [bt6], [bt_sms], [bt7], [bt8], [bt9], [bt10], [bt_cooldown], [bt_logs], [bt_broadcast], [bt11]])
    admin = 'Não'
    dono = 'Não'
    if message.chat.id == api.CredentialsChange.id_dono():
        dono = 'Sim'
    if api.Admin.verificar_admin(message.chat.id) == True:
        admin = 'Sim'
    txt = f'MENU DE CONFIGURACOES DO BOT\n\nAdmin: {admin}\nDono: {dono}'
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=txt, parse_mode='HTML', reply_markup=markup)

def configurar_cooldown_cancelamento(message):
    ativado = api.CooldownCancelamento.ativado()
    tempo = api.CooldownCancelamento.tempo_espera()
    
    limite_config = api.LimiteGeracao.carregar_config()
    limite_ativado = limite_config.get("ativado", True)
    max_tent = limite_config.get("max_tentativas_consecutivas", 8)
    tempo_minimo = limite_config.get("tempo_minimo_entre_geracoes", 30)
    tempo_ban = limite_config.get("tempo_ban_minutos", 15)
    ban_progressivo = limite_config.get("tempo_ban_progressivo", True)
    apenas_const = limite_config.get("apenas_constantes", False)
    
    status_cooldown = "✅ ATIVADO" if ativado else "❌ DESATIVADO"
    status_limite = "✅ ATIVADO" if limite_ativado else "❌ DESATIVADO"
    status_const = "(Apenas Não-Constantes)" if apenas_const else "(Todos)"
    ban_tipo = "Progressivo" if ban_progressivo else "Fixo"
    
    texto = (
        "⏱️ <b>CONFIGURAR COOLDOWN E LIMITE DE GERAÇÕES</b>\n\n"
        "<b>━ COOLDOWN DE CANCELAMENTO ━</b>\n"
        f"Status: {status_cooldown}\n"
        f"Tempo de Espera: {tempo}s\n\n"
        "<b>━ LIMITE DE GERAÇÕES CONSECUTIVAS ━</b>\n"
        f"Status: {status_limite} {status_const}\n"
        f"Máx Consecutivas: {max_tent}\n"
        f"Ban: {tempo_ban}min ({ban_tipo})\n"
        f"Reseta: SMS recebido OU {tempo_minimo}s de espera"
    )
    
    bt1 = InlineKeyboardButton('⏳ Cooldown Cancelamento', callback_data='menu_cooldown_cancelamento')
    bt2 = InlineKeyboardButton('🚫 Limite de Gerações', callback_data='menu_limite_geracao')
    bt3 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_painel_configuracoes')
    
    markup = InlineKeyboardMarkup([[bt1], [bt2], [bt3]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)

def menu_cooldown_cancelamento(message):
    ativado = api.CooldownCancelamento.ativado()
    tempo = api.CooldownCancelamento.tempo_espera()
    status_texto = "✅ ATIVADO" if ativado else "❌ DESATIVADO"
    
    texto = (
        "⏱️ <b>COOLDOWN DE CANCELAMENTO</b>\n\n"
        f"<b>Status:</b> {status_texto}\n"
        f"<b>Tempo de Espera:</b> {tempo} segundos\n\n"
        "<i>Quando ativado, o usuário precisa aguardar este tempo antes de poder cancelar um SMS.</i>"
    )
    
    bt1 = InlineKeyboardButton('🔄 ALTERNAR STATUS', callback_data='toggle_cooldown_status')
    bt2 = InlineKeyboardButton('⏲️ ALTERAR TEMPO', callback_data='alterar_tempo_cooldown')
    bt3 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_cooldown_menu')
    
    markup = InlineKeyboardMarkup([[bt1], [bt2], [bt3]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)

def menu_limite_geracao(message):
    config = api.LimiteGeracao.carregar_config()
    ativado = config.get("ativado", True)
    max_tent = config.get("max_tentativas_consecutivas", 8)
    tempo_minimo = config.get("tempo_minimo_entre_geracoes", 30)
    tempo_ban = config.get("tempo_ban_minutos", 15)
    ban_progressivo = config.get("tempo_ban_progressivo", True)
    max_ban = config.get("max_tempo_ban_minutos", 240)
    apenas_const = config.get("apenas_constantes", False)
    
    status_texto = "✅ ATIVADO" if ativado else "❌ DESATIVADO"
    status_const = "✅ SIM" if apenas_const else "❌ NÃO"
    status_progressivo = "✅ SIM" if ban_progressivo else "❌ NÃO"
    
    texto = (
        "🚫 <b>LIMITE DE GERAÇÕES CONSECUTIVAS</b>\n\n"
        f"<b>Status:</b> {status_texto}\n"
        f"<b>Máx Consecutivas:</b> {max_tent}\n"
        f"<b>Tempo Mín. entre gerações:</b> {tempo_minimo}s\n"
        f"<b>Ban Inicial:</b> {tempo_ban} min\n"
        f"<b>Ban Progressivo:</b> {status_progressivo}\n"
        f"<b>Ban Máximo:</b> {max_ban} min\n"
        f"<b>Apenas Não-Constantes:</b> {status_const}\n\n"
        "<i>📌 O contador reseta se:\n"
        f"• Usuário recebe SMS com sucesso\n"
        f"• Aguarda {tempo_minimo}s+ entre gerações\n\n"
        "🚫 Ban progressivo: 15→30→60→120→240 min</i>"
    )
    
    bt1 = InlineKeyboardButton('🔄 ALTERNAR STATUS', callback_data='toggle_limite_status')
    bt2 = InlineKeyboardButton('📊 MAX CONSECUTIVAS', callback_data='alterar_max_tentativas')
    bt3 = InlineKeyboardButton('⏱️ TEMPO MÍNIMO', callback_data='alterar_tempo_minimo_geracao')
    bt4 = InlineKeyboardButton('⏲️ TEMPO BAN INICIAL', callback_data='alterar_tempo_ban')
    bt5 = InlineKeyboardButton('📈 BAN PROGRESSIVO', callback_data='toggle_ban_progressivo')
    bt6 = InlineKeyboardButton('👥 APENAS NÃO-CONSTANTES', callback_data='toggle_apenas_constantes')
    bt7 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_cooldown_menu')
    
    markup = InlineKeyboardMarkup([[bt1], [bt2, bt3], [bt4, bt5], [bt6], [bt7]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)

def configurar_sms_provider(message):
    try:
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
    except Exception:
        data = {}

    provider = str(data.get("sms_provider", "herosms")).strip().lower()
    if provider not in ("herosms", "grizzly", "todos"):
        provider = "herosms"

    key_herosms = str(data.get("api-sms-herosms", "")).strip()
    key_grizzly = str(data.get("api-sms-grizzly", "")).strip()

    if provider == "todos":
        nome = "Todos os Provedores"
    elif provider == "herosms":
        nome = "Hero-SMS"
    else:
        nome = "GrizzlySMS"

    status_herosms = "OK" if key_herosms else "AVISO"
    status_grizzly = "OK" if key_grizzly else "AVISO"

    texto = (
        "📲 <b>PROVEDOR SMS (GLOBAL)</b>\n\n"
        f"🔎 <b>Atual:</b> {nome}\n\n"
        f"{status_herosms} <b>Chave Hero-SMS:</b> {'configurada' if key_herosms else 'não configurada'}\n"
        f"{status_grizzly} <b>Chave GrizzlySMS:</b> {'configurada' if key_grizzly else 'não configurada'}\n\n"
        "💡 <i>Trocar aqui muda o provedor do bot inteiro, sem precisar reiniciar.</i>\n"
        "🚀 <i>Modo 'Todos' tenta automaticamente múltiplos provedores se um falhar.</i>\n"
        "✍️ <i>Para cadastrar chaves:</i>\n"
        "<code>/mudar_api_herosms TOKEN</code>\n"
        "<code>/mudar_api_grizzly TOKEN</code>\n"
        "<code>/mudar_api TOKEN</code> (altera a chave do provedor atual)\n"
    )

    if provider == "herosms":
        bt1 = InlineKeyboardButton('✅ USAR HERO-SMS', callback_data='set_sms_provider herosms')
        bt2 = InlineKeyboardButton('❌ USAR GRIZZLYSMS', callback_data='set_sms_provider grizzly')
        bt3 = InlineKeyboardButton('❌ USAR TODOS DISPONÍVEIS', callback_data='set_sms_provider todos')
    elif provider == "grizzly":
        bt1 = InlineKeyboardButton('❌ USAR HERO-SMS', callback_data='set_sms_provider herosms')
        bt2 = InlineKeyboardButton('✅ USAR GRIZZLYSMS', callback_data='set_sms_provider grizzly')
        bt3 = InlineKeyboardButton('❌ USAR TODOS DISPONÍVEIS', callback_data='set_sms_provider todos')
    else:
        bt1 = InlineKeyboardButton('❌ USAR HERO-SMS', callback_data='set_sms_provider herosms')
        bt2 = InlineKeyboardButton('❌ USAR GRIZZLYSMS', callback_data='set_sms_provider grizzly')
        bt3 = InlineKeyboardButton('✅ USAR TODOS DISPONÍVEIS', callback_data='set_sms_provider todos')

    bt4 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_painel_configuracoes')
    markup = InlineKeyboardMarkup([[bt1], [bt2], [bt3], [bt4]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)

def gerenciar_servicos_destaque(message):
    servicos_destaque = api.ServicosDestaque.obter_servicos_destaque()
    
    try:
        with open('settings/traducoes_servicos.json', 'r', encoding='utf-8') as f:
            traducoes_data = json.load(f)
        traducoes = traducoes_data.get("traducoes", {})
    except:
        traducoes = {}
    
    texto = f'⭐ <b>SERVIÇOS EM DESTAQUE</b>\n\n'
    if servicos_destaque:
        texto += '<b>Serviços atualmente em destaque:</b>\n'
        for i, codigo in enumerate(servicos_destaque, 1):
            nome_servico = traducoes.get(codigo, codigo)
            texto += f'{i}. <code>{codigo}</code> - {nome_servico}\n'
    else:
        texto += 'Nenhum serviço em destaque configurado.\n'
    
    texto += '\n<i>Os serviços em destaque aparecem primeiro na lista de serviços.</i>'
    texto += '\n\n<b>💡 Dica:</b> Use os códigos dos serviços (ex: wa, tg, ig)'
    
    bt1 = InlineKeyboardButton('➕ ADICIONAR SERVIÇO', callback_data='adicionar_servico_destaque')
    bt2 = InlineKeyboardButton('➖ REMOVER SERVIÇO', callback_data='remover_servico_destaque')
    bt3 = InlineKeyboardButton('📋 LISTAR SERVIÇOS', callback_data='listar_servicos_destaque')
    bt4 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_painel_configuracoes')
    
    markup = InlineKeyboardMarkup([[bt1], [bt2], [bt3], [bt4]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)

def adicionar_servico_destaque_handler(message):
    codigo_servico = message.text.strip().lower()
    
    try:
        with open('settings/traducoes_servicos.json', 'r', encoding='utf-8') as f:
            traducoes_data = json.load(f)
        traducoes = traducoes_data.get("traducoes", {})
    except:
        traducoes = {}
    
    if codigo_servico not in traducoes:
        bot.reply_to(message, f"❌ Código '{codigo_servico}' não encontrado nas traduções. Use códigos válidos como: wa, tg, ig, fb, etc.")
        gerenciar_servicos_destaque(message)
        return
    
    if api.ServicosDestaque.adicionar_servico_destaque(codigo_servico):
        nome_servico = traducoes[codigo_servico]
        bot.reply_to(message, f"✅ Serviço '{codigo_servico}' ({nome_servico}) adicionado aos destaques com sucesso!")
    else:
        bot.reply_to(message, f"❌ Erro ao adicionar serviço '{codigo_servico}'. Pode já estar na lista.")
    
    gerenciar_servicos_destaque(message)

def remover_servico_destaque_handler(message):
    codigo_servico = message.text.strip().lower()
    
    try:
        with open('settings/traducoes_servicos.json', 'r', encoding='utf-8') as f:
            traducoes_data = json.load(f)
        traducoes = traducoes_data.get("traducoes", {})
    except:
        traducoes = {}
    
    if api.ServicosDestaque.remover_servico_destaque(codigo_servico):
        nome_servico = traducoes.get(codigo_servico, codigo_servico)
        bot.reply_to(message, f"✅ Serviço '{codigo_servico}' ({nome_servico}) removido dos destaques com sucesso!")
    else:
        bot.reply_to(message, f"❌ Erro ao remover serviço '{codigo_servico}'. Pode não estar na lista.")
    
    gerenciar_servicos_destaque(message)

def menu_edicoes(message):
    bt = InlineKeyboardButton('✍️ EDITAR TEXTOS', callback_data='configurar_textos')
    bt3 = InlineKeyboardButton('📣 EDITAR LOGS', callback_data='configurar_log')
    bt2 = InlineKeyboardButton('📥 EDITAR BOTÕES', callback_data='configurar_botoes')
    bt5 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_admin_acoes')
    markup = InlineKeyboardMarkup([[bt], [bt2], [bt3], [bt5]])
    text = 'Esse menu é exclusivo para as edições do bot, tais como: Edições de textos, edições de botões, edições das mensagens de log\n\n<i>Selecione abaixo o que deseja editar</i>'
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=text, parse_mode='HTML', reply_markup=markup)

def configurar_valores(message):
    porcentagem = api.InfoApi.porcentagem_lucro()
    texto = f'📊 <b>Porcentagem de lucro atual:</b> {porcentagem}%\n\n<i>Valor já convertido em BRL</i>'
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔄 ALTERAR PORCENTAGEM', callback_data='alterar_porcentagem')], [InlineKeyboardButton(f'{api.Botoes.voltar()}', callback_data='admin_configuracoes')]]))

def alterar_porcentagem(message):
    nova_porcentagem = message.text
    porcent = nova_porcentagem.replace('%', '').strip()
    api.InfoApi.mudar_porcentagem_lucro(porcent)
    bot.reply_to(message, "Alterado com sucesso!")

def configuracoes_geral(message):
    texto = f'<i>Use os botões abaixo para configurar seu bot:</i>\n👤 <b>LINK DO SUPORTE ATUAL: {api.CredentialsChange.SuporteInfo.link_suporte()}</b>'
    bt = InlineKeyboardButton('🔴 MANUTENÇÃO (off)', callback_data='manutencao')
    if api.CredentialsChange.status_manutencao() == True:
        bt = InlineKeyboardButton('🟢 MANUTENÇÃO (on)', callback_data='manutencao')
    b = InlineKeyboardButton('🤖 REINICIAR BOT 🤖', callback_data='reiniciar_bot')
    bt1 = InlineKeyboardButton('🎧 MUDAR SUPORTE', callback_data='suporte')
    bt4 = InlineKeyboardButton('📸 MUDAR FOTO DO MENU START', callback_data='mudar_foto_menu')
    bt5 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_painel_configuracoes')
    markup = InlineKeyboardMarkup([[b], [bt], [bt1], [bt4], [bt5]])
    safe_edit_message(chat_id=message.chat.id, text=texto, message_id=message.message_id, reply_markup=markup, parse_mode='HTML')

def trocar_suporte(message, idcall):
    suporte = message.text
    api.CredentialsChange.SuporteInfo.mudar_link_suporte(str(suporte))
    safe_answer_callback(idcall, "Suporte alterado com sucesso!", show_alert=True)

def mudar_foto_menu(message):
    if message.content_type == 'photo':
        photo_info = message.photo[-1]
        photo = photo_info.file_id
        
        file_size = photo_info.file_size if hasattr(photo_info, 'file_size') else "Desconhecido"
        width = photo_info.width
        height = photo_info.height
        
        if not hasattr(bot, 'temp_photo_data'):
            bot.temp_photo_data = {}
        temp_id = f"photo_{message.chat.id}_{int(time.time())}"
        bot.temp_photo_data[temp_id] = photo
        
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("CONFIRMAR", callback_data=f'c-p-m-photo {temp_id}')]])
        caption = f"<b>Essa será a nova foto do menu inicial, você confirma?</b>\n\n📏 <b>Dimensões:</b> {width}x{height}\n💾 <b>Tamanho:</b> {file_size} bytes"
        bot.send_photo(message.chat.id, photo, caption=caption, parse_mode='HTML', reply_markup=markup)
    elif message.text and message.text.startswith('htt'):
        url = message.text
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("CONFIRMAR", callback_data=f'c-p-m-url {url}')]])
        bot.send_photo(message.chat.id, url, caption="<b>Essa será a nova foto do menu inicial, você confirma?</b>\n\n💡 <b>Dica:</b> Para melhor qualidade, envie a foto diretamente em vez de URL", parse_mode='HTML', reply_markup=markup)
    else:
        bot.reply_to(message, "❌ <b>Formato inválido!</b>\n\n✅ <b>Envie:</b>\n• Uma foto diretamente\n• Uma URL de imagem (https://...)\n\n💡 <b>Dica:</b> Para melhor qualidade, envie a foto diretamente!", parse_mode='HTML')

def configurar_admins(message):
    texto = f'🅰️ <b>PAINEL CONFIGURAR ADMIN</b>\n\n👮 Administradores: {api.Admin.quantidade_admin()}\n<i>Use os botões abaixo para fazer as alterações necessárias</i>'
    bt = InlineKeyboardButton('➕ ADICIONAR ADM', callback_data='adicionar_adm')
    bt2 = InlineKeyboardButton('🚮 REMOVER ADM', callback_data='remover_adm')
    bt3 = InlineKeyboardButton('📃 LISTA DE ADM', callback_data='lista_adm')
    bt4 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_painel_configuracoes')
    markup = InlineKeyboardMarkup([[bt], [bt2], [bt3], [bt4]])
    safe_edit_message(chat_id=message.chat.id, text=texto, message_id=message.message_id, parse_mode='HTML', reply_markup=markup)

def adicionar_adm(message):
    try:
        id_admin = message.text
        api.Admin.add_admin(id_admin)
        bot.reply_to(message, f"O usuario: {id_admin} foi feito admin!")
    except:
        bot.reply_to(message, "Erro ao promover para adm.")

def remover_adm(message):
    try:
        id = message.text
        api.Admin.remover_admin(id)
        bot.reply_to(message, f"Adm {id} foi feito um usuario comum novamente.")
    except:
        bot.reply_to(message, "Falha ao remover o adm.")

def configurar_afiliados(message):
    texto = f'◎ ══════ ❈ ══════ ◎\n🗞 <b>PORCENTAGEM POR INDICAÇÃO</b>\n◎ ══════ ❈ ══════ ◎\nEssa é a porcentagem de ganhos que o usuário recebe cada vez que o seu afiliado fizer uma recarga.\n┕━━━━╗✹╔━━━━┙'
    bt = InlineKeyboardButton('🗞 PORCENTAGEM POR RECARGA', callback_data='porcentagem_por_indicacao')
    bt2 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_painel_configuracoes')
    markup = InlineKeyboardMarkup([[bt], [bt2]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)

def porcentagem_por_indicacao(message):
    try:
        pontos = message.text
        api.AfiliadosInfo.mudar_porcentagem_por_indicacao(pontos)
        bot.reply_to(message, f"Alterado com sucesso! Agora toda vez que um usuário recarregar, quem indicou ele ganhará {pontos}% da recarga.")
    except Exception as e:
        print(e)
        bot.reply_to(message, "Falha ao alterar a quantidade de pontos, verifique se enviou um número aceitavel.")

def pontos_minimo_converter(message):
    try:
        min = message.text
        api.AfiliadosInfo.trocar_minimo_pontos_pra_saldo(min)
        bot.reply_to(message, f"Feito! Agora os usuarios precisam ter {min} pontos para poder converter em saldo.")
    except:
        bot.reply_to(message, f"Erro ao alterar a quantidade de pontos, verifique se enviou um número aceitavel.")

def multiplicador_para_converter(message):
    try:
        mult = message.text
        api.AfiliadosInfo.trocar_multiplicador_pontos(mult)
        bot.reply_to(message, "Multiplicador alterado com sucesso!")
    except:
        bot.reply_to(message, "Falha ao alterar o multiplicador, verifique se enviou um número aceitavel.")

def salvar_tempo_cooldown(message):
    try:
        tempo = int(message.text)
        if tempo < 0:
            bot.reply_to(message, "❌ O tempo deve ser um número maior ou igual a 0!")
            return
        api.CooldownCancelamento.mudar_tempo_espera(tempo)
        bot.reply_to(message, f"✅ Tempo de cooldown alterado para {tempo} segundos com sucesso!")
    except ValueError:
        bot.reply_to(message, "❌ Por favor, envie um número válido em segundos.")
    except Exception as e:
        print(f"Erro ao salvar tempo cooldown: {e}")
        bot.reply_to(message, "❌ Erro ao salvar o tempo de cooldown.")

def salvar_max_tentativas(message):
    try:
        max_tent = int(message.text)
        if max_tent < 1 or max_tent > 20:
            bot.reply_to(message, "❌ O valor deve estar entre 1 e 20!")
            return
        config = api.LimiteGeracao.carregar_config()
        config["max_tentativas_consecutivas"] = max_tent
        api.LimiteGeracao.salvar_config(config)
        bot.reply_to(message, f"✅ Máximo de tentativas consecutivas alterado para {max_tent}!")
    except ValueError:
        bot.reply_to(message, "❌ Por favor, envie um número válido.")
    except Exception as e:
        print(f"Erro ao salvar max tentativas: {e}")
        bot.reply_to(message, "❌ Erro ao salvar configuração.")

def salvar_tempo_minimo_geracao(message):
    try:
        tempo = int(message.text)
        if tempo < 10 or tempo > 300:
            bot.reply_to(message, "❌ O valor deve estar entre 10 e 300 segundos!")
            return
        config = api.LimiteGeracao.carregar_config()
        config["tempo_minimo_entre_geracoes"] = tempo
        api.LimiteGeracao.salvar_config(config)
        bot.reply_to(message, f"✅ Tempo mínimo entre gerações alterado para {tempo} segundos!")
    except ValueError:
        bot.reply_to(message, "❌ Por favor, envie um número válido.")
    except Exception as e:
        print(f"Erro ao salvar tempo mínimo: {e}")
        bot.reply_to(message, "❌ Erro ao salvar configuração.")

def configurar_usuarios(message):
    texto = f'◎ ══════ ❈ ══════ ◎\n📪 <b>TRANSMITIR A TODOS</b>\n◎ ══════ ❈ ══════ ◎\nEnvia uma mensagem para todos os usuários registrados no bot. 📬✉️\nApós clicar, envie o texto que quer transmitir ou a foto. Para enviar uma foto com texto, basta colocar o texto na legenda da imagem. 📷🖋️\n┕━━━━╗✹╔━━━━┙\n\n\n◎ ══════ ❈ ══════ ◎\n🔎 <b>PESQUISAR USUÁRIO</b>\n◎ ══════ ❈ ══════ ◎\nSe este usuário estiver registrado no bot, vai abrir as configurações de edição desse usuário. 💼🔧\nVocê poderá editar o saldo, ver o histórico de compras, e todas as informações dele. 📈📋\n┕━━━━╗✹╔━━━━┙\n\n\n◎ ══════ ❈ ══════ ◎\n🎁 <b>BÔNUS DE REGISTRO</b>\n◎ ══════ ❈ ══════ ◎\nBônus atual: R${api.CredentialsChange.BonusRegistro.bonus():.2f}\n<i>Bônus de registro é o valor que cada usuário novo ganhará apenas por se registrar, é um bônus de boas-vindas.</i>\nPara não dar bônus nenhum, deixe em 0\n┕━━━━╗✹╔━━━━┙'
    bt = InlineKeyboardButton('📫 TRANSMITIR A TODOS', callback_data='transmitir_todos')
    bt2 = InlineKeyboardButton('🔎 PESQUISAR USUARIO', callback_data='pesquisar_usuario')
    bt3 = InlineKeyboardButton('🎁 BONUS DE REGISTRO', callback_data='mudar_bonus_registro')
    bt4 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_painel_configuracoes')
    markup = InlineKeyboardMarkup([[bt], [bt2], [bt3], [bt4]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)

def transmitir_todos(message):
    api.FuncaoTransmitir.zerar_infos()
    bt = InlineKeyboardButton('➕ ADD BOTAO ➕', callback_data='add_botao')
    bt2 = InlineKeyboardButton('✅ CONFIRMAR ENVIO', callback_data='confirmar_envio')
    markup = InlineKeyboardMarkup([[bt], [bt2]])
    if message.content_type == 'photo':
        photo = message.photo[0].file_id
        api.FuncaoTransmitir.adicionar_foto(photo)
        api.FuncaoTransmitir.adicionar_texto(message.caption)
        bot.send_photo(message.chat.id, photo=photo, caption=message.caption, reply_markup=markup, parse_mode='HTML')
    elif message.content_type == 'text':
        api.FuncaoTransmitir.adicionar_texto(message.text)
        bot.send_message(message.chat.id, text=message.text, reply_markup=markup, parse_mode='HTML')
    else:
        bot.reply_to(message, "Este tipo de mensagem ainda não está disponível para transmitir.")

def add_botao(message):
    try:
        text = message.text
        s = text.split('\n')
        markup = InlineKeyboardMarkup()
        for elemento in s:
            botoes = []
            separar = elemento.split('&&')
            for botao in separar:
                sep = botao.split('-')
                nome = sep[0].strip()
                url = sep[1].strip()
                botoes.append(InlineKeyboardButton(f'{nome}', url=f'{url}'))
            markup.row(*botoes)
        api.FuncaoTransmitir.adicionar_markup(markup)
        bt2 = InlineKeyboardButton('✅ CONFIRMAR ENVIO', callback_data='confirmar_envio')
        markup.row(bt2)
        if markup != None:
            texto = api.FuncaoTransmitir.pegar_texto()
            photo = api.FuncaoTransmitir.pegar_foto()
            if texto != None and photo == None:
                bot.send_message(message.chat.id, texto, reply_markup=markup, parse_mode='HTML')
            elif photo != None and texto == None:
                bot.send_photo(message.chat.id, photo, reply_markup=markup, parse_mode='HTML')
            elif photo != None and texto != None:
                bot.send_photo(message.chat.id, photo, caption=texto, reply_markup=markup, parse_mode='HTML')
            else:
                bot.reply_to(message, "Error!")
    except Exception as e:
        bot.reply_to(message, "Ocorreu um erro ao processar, verifique se enviou o nome e a URL no formato correto.")
        print(e)

enviando_transmissao = False

def confirmar_envio(message):
    global enviando_transmissao
    markup1 = api.FuncaoTransmitir.pegar_markup()
    markup = InlineKeyboardMarkup()
    if markup1 != None:
        for bt in markup1:
            buttons = []
            for b in bt:
                buttons.append(InlineKeyboardButton(b["text"], url=b["url"]))
            markup.row(*buttons)
    else:
        markup = None
    texto = api.FuncaoTransmitir.pegar_texto()
    photo = api.FuncaoTransmitir.pegar_foto()
    with open('database/users.json', 'r') as f:
        data = json.load(f)
    enviando_transmissao = True
    msg = bot.send_message(message.chat.id, "<i>Enviando transmissão</i>", parse_mode='HTML')
    threading.Thread(target=enviar_status_transmissao, args=(msg,)).start()
    for user in data["users"]:
        try:
            if photo == None:
                bot.send_message(user["id"], texto, parse_mode='HTML', reply_markup=markup)
            else:
                bot.send_photo(user["id"], photo, caption=texto, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            print(e)
            pass
    enviando_transmissao = False

def enviar_status_transmissao(message):
    global enviando_transmissao
    while True:
        if enviando_transmissao == False:
            try:
                bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="✅ <b>Transmissão finalizada!</b>", parse_mode='HTML')
            except:
                pass
            break
        else:
            try:
                time.sleep(1.2)
                bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="<i>Enviando transmissão.</i>", parse_mode='HTML')
                time.sleep(1.2)
                bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="<i>Enviando transmissão..</i>", parse_mode='HTML')
                time.sleep(1.2)
                bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="<i>Enviando transmissão...</i>", parse_mode='HTML')
            except:
                break
    return

def pesquisar_usuario(message):
    id = message.text
    if api.InfoUser.verificar_usuario(id) == True:
        try:
            user_info = bot.get_chat(id)
            first_name = user_info.first_name or "N/A"
            last_name = user_info.last_name or ""
            full_name = f"{first_name} {last_name}".strip()
            username = f"@{user_info.username}" if user_info.username else "Sem username"
        except Exception as e:
            print(f"⚠️ Erro ao buscar info do usuário {id}: {e}")
            full_name = "N/A"
            username = "N/A"
        
        texto = (
            f'🔎 <b>USUÁRIO ENCONTRADO</b> ✅\n\n'
            f'🕵️ <b>INFORMAÇÕES</b> 🕵️\n'
            f'👤 <b>NOME:</b> <code>{full_name}</code>\n'
            f'🔖 <b>USERNAME:</b> <code>{username}</code>\n'
            f'📛 <b>ID:</b> <code>{id}</code>\n'
            f'💰 <b>SALDO:</b> <code>{api.InfoUser.saldo(id):.2f}</code>\n'
            f'🛒 <b>ACESSOS COMPRADOS:</b> <code>{api.InfoUser.total_compras(id)}</code>\n'
            f'💠 <b>PIX INSERIDOS:</b> <code>R${api.InfoUser.pix_inseridos(id):.2f}</code>\n'
            f'👥 <b>INDICADOS:</b> <code>{api.InfoUser.quantidade_afiliados(id)}</code>\n'
            f'🎁 <b>GIFT RESGATADO:</b> <code>R${api.InfoUser.gifts_resgatados(id):.2f}</code>'
        )
        
        bt = InlineKeyboardButton('🧑‍⚖️ Banir', callback_data=f'banir {id}')
        bt2 = InlineKeyboardButton('💰 MUDAR SALDO', callback_data=f'mudar_saldo {id}')
        bt3 = InlineKeyboardButton('📥 BAIXAR HISTORICO', callback_data=f'baixar_historico {id}')
        markup = InlineKeyboardMarkup([[bt], [bt2], [bt3]])
        if api.InfoUser.verificar_ban(id) == True:
            bt = InlineKeyboardButton('🧑‍⚖️ DESBANIR', callback_data=f'banir {id}')
            markup = InlineKeyboardMarkup([[bt]])
        bot.send_message(chat_id=message.chat.id, text=texto, parse_mode='HTML', reply_markup=markup)
    else:
        bot.reply_to(message, "Usuario não foi encontrado.")

def mudar_saldo(message, id):
    saldo = message.text
    try:
        api.InfoUser.mudar_saldo(id, saldo)
        bot.reply_to(message, "Saldo alterado com sucesso!")
    except:
        bot.reply_to(message, "Falha ao alterar, verifique se enviou um valor valido.")

def monitoramentozucpayconta(call):
    if not api.CredentialsChange.PlataformaPix.status_zucpay():
        safe_answer_callback(call, "❌ Zucpay não está ativo!", show_alert=True)
        return
    
    bt = InlineKeyboardButton('🔄 SALDO ZUCPAY', callback_data='ver_saldo_zucpay')
    bt2 = InlineKeyboardButton('📊 EXTRATO', callback_data='extrato_zucpay')
    bt3 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_paineladm')
    markup = InlineKeyboardMarkup([[bt], [bt2], [bt3]])
    
    texto = "💎 <b>MONITORAMENTO ZUCPAY</b>\n\nUse os botões abaixo para consultar saldo e extrato da sua conta Zucpay."
    
    safe_edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=texto,
        parse_mode='HTML',
        reply_markup=markup
    )

def ver_saldo_zucpay(call):
    try:
        zucpay = api.ApiZucpayInfo()
        saldo_info = zucpay.consultar_saldo()
        
        if saldo_info:
            texto = (
                f"💰 <b>SALDO ZUCPAY</b>\n\n"
                f"💵 <b>Saldo disponível:</b> R${saldo_info['balance']:.2f}\n"
                f"📥 <b>Total depositado:</b> R${saldo_info['total_deposited']:.2f}\n"
                f"📤 <b>Total sacado:</b> R${saldo_info['total_withdrawn']:.2f}\n"
                f"🪙 <b>Moeda:</b> {saldo_info['currency']}\n\n"
                f"🔄 <i>Dados atualizados em tempo real</i>"
            )
        else:
            texto = "❌ Não foi possível consultar o saldo da conta Zucpay. Verifique sua chave API."
        
        bt_voltar = InlineKeyboardButton('🔙 VOLTAR', callback_data='monitoramentozucpayconta')
        markup = InlineKeyboardMarkup([[bt_voltar]])
        
        safe_edit_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=texto,
            parse_mode='HTML',
            reply_markup=markup
        )
    except Exception as e:
        print(f"❌ Erro ao consultar saldo Zucpay: {e}")
        safe_answer_callback(call, "❌ Erro ao consultar saldo. Tente novamente.", show_alert=True)

def extrato_zucpay(call):
    try:
        zucpay = api.ApiZucpayInfo()
        # Implementar consulta de extrato se disponível
        
        texto = (
            f"📊 <b>EXTRATO ZUCPAY</b>\n\n"
            f"ℹ️ Para ver o extrato completo, acesse o painel Zucpay ou aguarde implementação do webhook.\n\n"
            f"🔗 <b>Endpoint:</b> /webhook/zucpay-sms"
        )
        
        bt_voltar = InlineKeyboardButton('🔙 VOLTAR', callback_data='monitoramentozucpayconta')
        markup = InlineKeyboardMarkup([[bt_voltar]])
        
        safe_edit_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=texto,
            parse_mode='HTML',
            reply_markup=markup
        )
    except Exception as e:
        print(f"❌ Erro ao consultar extrato Zucpay: {e}")
        safe_answer_callback(call, "❌ Erro ao consultar extrato. Tente novamente.", show_alert=True)

def configurar_pix(message):
    # Ler valores diretamente do arquivo de credenciais
    try:
        with open('settings/credenciais.json', 'r') as f:
            creds = json.load(f)
        
        token_zucpay = creds.get('token_zucpay', 'Não configurado')
        deposito_minimo = creds.get('min_pix', 3.0)
        deposito_maximo = creds.get('max_pix', 2000.0)
        expiracao = creds.get('expiracao_pix', 20)
        bonus = creds.get('bonus_pix', 10)
        bonus_min = creds.get('bonus_pix_min', 20)
        
    except Exception as e:
        print(f"Erro ao ler credenciais: {e}")
        token_zucpay = 'Erro ao ler'
        deposito_minimo = 3.0
        deposito_maximo = 2000.0
        expiracao = 20
        bonus = 10
        bonus_min = 20
    
    # Mascarar o token para exibição
    if token_zucpay not in ['Não configurado', 'Erro ao ler'] and len(token_zucpay) > 10:
        token_mostrar = token_zucpay[:8] + '...' + token_zucpay[-4:]
    elif token_zucpay == 'Não configurado':
        token_mostrar = 'Não configurado (use /mudar_token_zucpay)'
    else:
        token_mostrar = token_zucpay
    
    texto = f'🔑 <b>TOKEN ZUCPAY:</b> <code>{token_mostrar}</code>\n🔻 <b>DEPÓSITO MÍNIMO:</b> <code>R${deposito_minimo:.2f}</code>\n❗️ <b>DEPÓSITO MÁXIMO:</b> <code>R${deposito_maximo:.2f}</code>\n⏰ <b>TEMPO DE EXPIRAÇÃO:</b> <i>{expiracao} Minutos</i>\n🔶 <b>BÔNUS DE DEPÓSITO:</b> <code>{bonus}%</code>\n🔷 <b>DEPÓSITO MÍNIMO PARA GANHAR O BÔNUS:</b> R${bonus_min:.2f}'
    
    bt = InlineKeyboardButton('🔴 PIX MANUAL', callback_data='trocar_pix_manual')
    bt2 = InlineKeyboardButton('🔴 PIX AUTOMATICO', callback_data='trocar_pix_automatico')
    
    if api.CredentialsChange.StatusPix.pix_manual() == True:
        bt = InlineKeyboardButton('🟢 PIX MANUAL', callback_data='trocar_pix_manual')
    if api.CredentialsChange.StatusPix.pix_auto() == True:
        bt2 = InlineKeyboardButton('🟢 PIX AUTOMATICO', callback_data='trocar_pix_automatico')
    
    bt3 = InlineKeyboardButton('🟢 PIX ZUCPAY', callback_data='mudar_pix_zucpay_status')
    bt7 = InlineKeyboardButton('🔻 MUDAR DEPOSITO MIN', callback_data='mudar_deposito_minimo')
    bt8 = InlineKeyboardButton('❗️ MUDAR DEPOSITO MAX', callback_data='mudar_deposito_maximo')
    bt9 = InlineKeyboardButton('🔶 MUDAR BONUS', callback_data='mudar_bonus')
    bt10 = InlineKeyboardButton('🔷 MUDAR MIN PARA BONUS', callback_data='mudar_min_bonus')
    bt11 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_painel_configuracoes')
    
    markup = InlineKeyboardMarkup([[bt, bt2], [bt3], [bt7], [bt8], [bt9], [bt10], [bt11]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)

def mudar_token_zucpay(message):
    try:
        token = message.text.strip()
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["token_zucpay"] = token
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
        bot.reply_to(message, "Token Zucpay alterado com sucesso!")
    except Exception as e:
        print(e)
        bot.reply_to(message, f"Falha ao alterar token Zucpay: {e}")

def mudar_deposito_minimo(message):
    try:
        novo_min = float(message.text)
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["min_pix"] = novo_min
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
        bot.reply_to(message, f"Depósito mínimo alterado para R${novo_min:.2f}!")
    except Exception as e:
        print(e)
        bot.reply_to(message, "Falha ao alterar. Envie um número válido!")

def mudar_deposito_maximo(message):
    try:
        novo_max = float(message.text)
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["max_pix"] = novo_max
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
        bot.reply_to(message, f"Depósito máximo alterado para R${novo_max:.2f}!")
    except Exception as e:
        print(e)
        bot.reply_to(message, "Falha ao alterar. Envie um número válido!")

def mudar_expiracao(message):
    if message.text.isdigit() == True:
        expiracao = int(message.text)
        if expiracao < 15:
            bot.reply_to(message, "O tempo de expiracao deve ser maior do que 15 minutos!")
            return
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["expiracao_pix"] = expiracao
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
        bot.reply_to(message, f"Tempo de expiração alterado para {expiracao} minutos!")
    else:
        bot.reply_to(message, "Envie apenas digitos!")

def mudar_bonus(message):
    try:
        p = message.text
        p = p.replace('%', '')
        p = p.strip()
        novo_bonus = int(p)
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["bonus_pix"] = novo_bonus
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
        bot.reply_to(message, f"Bônus alterado para {novo_bonus}%!")
    except Exception as e:
        print(e)
        bot.reply_to(message, "Falha ao alterar. Envie um número válido!")

def mudar_min_bonus(message):
    try:
        novo_min = float(message.text)
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["bonus_pix_min"] = novo_min
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
        bot.reply_to(message, f"Valor mínimo para bônus alterado para R${novo_min:.2f}!")
    except Exception as e:
        print(e)
        bot.reply_to(message, "Falha ao Envie um número válido!")
 
def configurar_textos(message):
    texto = 'Selecione o menu que deseja editar o texto:'
    bt = InlineKeyboardButton('🏠 MENU START', callback_data='mudar_texto start')
    bt2 =  InlineKeyboardButton('👤 MENU PERFIL', callback_data='mudar_texto perfil')
    bt3 = InlineKeyboardButton('💰 MENU ADD SALDO', callback_data='mudar_texto addsaldo')
    bt4 = InlineKeyboardButton('📱 MENSAGEM PIX MANUAL', callback_data='mudar_texto pixmanual')
    bt5 = InlineKeyboardButton('🤖 MENSAGEM PIX AUTOMATICO', callback_data='mudar_texto pixauto')
    bt6 = InlineKeyboardButton('⏰ PAGAMENTO EXPIRADO', callback_data='mudar_texto pagamento_expirado')
    bt7 = InlineKeyboardButton('✅ PAGAMENTO APROVADO', callback_data='mudar_texto pagamento_aprovado')
    bt8 = InlineKeyboardButton('🛒 MENU COMPRAR', callback_data='mudar_texto comprar')
    bt9 = InlineKeyboardButton('📋 MENU EXIBIR SERVICOS', callback_data='mudar_texto exibir_servico')
    bt10 = InlineKeyboardButton('📨 MENSAGEM COM ENTREGA DO NUMERO', callback_data='mudar_texto mensagem_comprou')
    bt11 = InlineKeyboardButton('📜 TERMOS', callback_data='mudar_texto termos')
    bt12 = InlineKeyboardButton('❓ AJUDA', callback_data='mudar_texto ajuda')
    bt13 = InlineKeyboardButton('🆔 ID', callback_data='mudar_texto id')
    bt14 = InlineKeyboavrdButton('💳 SALDO', callback_data='mudar_texto saldo')
    bt15 = InlineKeyboardButton('👥 AFILIADOS', callback_data='mudar_texto afiliados')
    bt16 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_menuedicoes')
    markup = InlineKeyboardMarkup([[bt], [bt2], [bt3], [bt4], [bt5], [bt6], [bt7], [bt8], [bt9], [bt10], [bt11], [bt12], [bt13], [bt14], [bt15], [bt16]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)

def mudar_texto(message, tipo):
    if tipo == 'start':
        api.MudarTexto.start(message.text)
    if tipo == 'perfil':
        api.MudarTexto.perfil(message.text)
    if tipo == 'addsaldo':
        api.MudarTexto.adicionar_saldo(message.text)
    if tipo == 'pixmanual':
        api.MudarTexto.pix_manual(message.text)
    if tipo == 'pixauto':
        api.MudarTexto.pix_automatico(message.text)
    if tipo == 'pagamento_expirado':
        api.MudarTexto.pagamento_expirado(message.text)
    if tipo == 'pagamento_aprovado':
        api.MudarTexto.pagamento_aprovado(message.text)
    if tipo == 'comprar':
        api.MudarTexto.menu_comprar(message.text)
    if tipo == 'exibir_servico':
        api.MudarTexto.exibir_servico(message.text)
    if tipo == 'mensagem_comprou':
        api.MudarTexto.mensagem_comprou(message.text)
    if tipo == 'termos':
        api.MudarTexto.termos(message.text)
    if tipo == 'ajuda':
        api.MudarTexto.ajuda(message.text)
    if tipo == 'id':
        api.MudarTexto.id(message.text)
    if tipo == 'afiliados':
        api.MudarTexto.afiliados(message.text)
    if tipo == 'saldo':
        api.MudarTexto.saldo(message.text)
    bot.reply_to(message, "Alterado com sucesso!")

def mudar_botao(message, tipo):
    if tipo == 'comprar':
        api.MudarBotao.comprar(message.text)
    if tipo == 'perfil':
        api.MudarBotao.perfil(message.text)
    if tipo == 'paises':
        api.MudarBotao.paises(message.text)
    if tipo == 'addsaldo':
        api.MudarBotao.addsaldo(message.text)
    if tipo == 'suporte':
        api.MudarBotao.suporte(message.text)
    if tipo == 'comprarlogin':
        api.MudarBotao.comprar_login(message.text)
    if tipo == 'pixmanual':
        api.MudarBotao.pix_manual(message.text)
    if tipo == 'pixautomatico':
        api.MudarBotao.pix_automatico(message.text)
    if tipo == 'download':
        api.MudarBotao.download_historico(message.text)
    if tipo == 'trocarpontos':
        api.MudarBotao.trocar_pontos_por_saldo(message.text)
    if tipo == 'aguardando_pagamento':
        api.MudarBotao.aguardando_pagamento(message.text)
    bot.reply_to(message, "Alterado com sucesso!")

def gift_card(message):
    bt = InlineKeyboardButton('🎁 GERAR GIFT CARD', switch_inline_query_current_chat='CREATEGIFT 1')
    bt2 = InlineKeyboardButton('🎁 GERAR VARIOS GIFT 🎁', switch_inline_query_current_chat='CREATEGIFT 1 10')
    bt3 = InlineKeyboardButton('♟ GIFTS CRIADOS', callback_data='gifts_criados')
    bt4 = InlineKeyboardButton('🔙 VOLTAR', callback_data='admin_transacoes')
    markup = InlineKeyboardMarkup([[bt], [bt2], [bt3], [bt4]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text='<i>Selecione a opção desejada:</i>', parse_mode='HTML', reply_markup=markup)

@bot.inline_handler(lambda query: query.query.startswith('CREATEGIFT '))
def create_gift_card(inline_query):
    print(f"=== DEBUG CREATEGIFT ===")
    print(f"Query recebida: '{inline_query.query}'")
    print(f"ID do usuário: {inline_query.from_user.id}")
    print(f"Username: {inline_query.from_user.username}")
    
    is_admin = api.Admin.verificar_admin(inline_query.from_user.id)
    is_owner = int(api.CredentialsChange.id_dono()) == int(inline_query.from_user.id)
    print(f"É admin: {is_admin}")
    print(f"É dono: {is_owner}")
    
    if is_admin == False and is_owner == False:
        print("Usuário sem permissão, retornando...")
        return
    
    query_parts = inline_query.query.split()
    print(f"Partes da query: {query_parts}")
    print(f"Número de partes: {len(query_parts)}")
    
    if len(query_parts) == 2:
        print("=== GERANDO GIFT CARD ÚNICO ===")
        value = query_parts[1]
        print(f"Valor solicitado: {value}")
        
        try:
            valor, codigo = gerar_gift_card(value)
            print(f"Gift card gerado - Valor: {valor}, Código: {codigo}")
            
            txt = f'🎁 <b>GIFT CARD GERADO</b> 🎁\n\n💰 <b>Valor:</b> <i>R${value}</i>\n🤑 <b>Codigo:</b> <code>{codigo}</code>'
            title = f"Criar gift card de {value}"
            description = f"Clique aqui para criar um gift card de {value}."
            
            print(f"Texto gerado: {txt}")
            print(f"Título: {title}")
            print(f"Descrição: {description}")
            
            reply_markup = telebot.types.InlineKeyboardMarkup()
            button_text = "📝 Resgatar agora"
            button = telebot.types.InlineKeyboardButton(button_text, callback_data=f'resgatar {codigo}')
            reply_markup.add(button)
            
            result_id = '1'
            print(f"Result ID: {result_id}")
            
            try:
                result = telebot.types.InlineQueryResultArticle(
                    id=result_id, 
                    title=title, 
                    description=description, 
                    input_message_content=telebot.types.InputTextMessageContent(txt, parse_mode='HTML'), 
                    reply_markup=reply_markup, 
                    thumbnail_url='https://cdn-icons-png.flaticon.com/512/612/612886.png'
                )
                print("Result criado com thumbnail_url")
            except Exception as e:
                print(f"Erro ao criar result com thumbnail_url: {e}")
                result = telebot.types.InlineQueryResultArticle(
                    id=result_id, 
                    title=title, 
                    description=description, 
                    input_message_content=telebot.types.InputTextMessageContent(txt, parse_mode='HTML'), 
                    reply_markup=reply_markup, 
                    thumb_url='https://cdn-icons-png.flaticon.com/512/612/612886.png'
                )
                print("Result criado com thumb_url")
            
            print("Enviando resposta inline...")
            bot.answer_inline_query(inline_query.id, [result], cache_time=0)
            print("Resposta inline enviada com sucesso!")
            
        except Exception as e:
            print(f"Erro ao gerar gift card único: {e}")
            print(f"Tipo de erro: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            
    else:
        print("=== GERANDO MÚLTIPLOS GIFT CARDS ===")
        value = query_parts[1]
        quantidade = query_parts[2]
        print(f"Valor: {value}, Quantidade: {quantidade}")
        
        try:
            codigo = gerar_muito_gift(quantidade, value)
            print(f"Códigos gerados: {codigo}")
            
            txt = f'🎁 <b>GIFT CARD GERADO</b> 🎁\n\n💰 <b>Valor:</b> <i>R${value}</i>\n🤑 <b>Codigos:</b>\n<code>{codigo}</code>'
            title = f"Criar {quantidade} gifts cards de R${float(value):.2f}"
            description = f"Clique aqui para criar {quantidade} gift card de R${float(value):.2f}."
            
            print(f"Texto gerado: {txt}")
            print(f"Título: {title}")
            print(f"Descrição: {description}")
            
            result_id = '3'
            print(f"Result ID: {result_id}")
            
            try:
                result = telebot.types.InlineQueryResultArticle(
                    id=result_id, 
                    title=title, 
                    description=description, 
                    input_message_content=telebot.types.InputTextMessageContent(txt, parse_mode='HTML'), 
                    thumbnail_url='https://cdn-icons-png.flaticon.com/512/1261/1261149.png'
                )
                print("Result criado com thumbnail_url")
            except Exception as e:
                print(f"Erro ao criar result com thumbnail_url: {e}")
                result = telebot.types.InlineQueryResultArticle(
                    id=result_id, 
                    title=title, 
                    description=description, 
                    input_message_content=telebot.types.InputTextMessageContent(txt, parse_mode='HTML'), 
                    thumb_url='https://cdn-icons-png.flaticon.com/512/1261/1261149.png'
                )
                print("Result criado com thumb_url")
            
            print("Enviando resposta inline...")
            bot.answer_inline_query(inline_query.id, [result])
            print("Resposta inline enviada com sucesso!")
            
        except Exception as e:
            print(f"Erro ao gerar múltiplos gift cards: {e}")
            print(f"Tipo de erro: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
    
    print("=== FIM DEBUG CREATEGIFT ===")

def gerar_muito_gift(quantidade, valor):
    print(f"=== DEBUG GERAR MUITO GIFT ===")
    print(f"Quantidade: {quantidade}, Valor: {valor}")
    codigos = ''
    for i in range(int(quantidade)):
        print(f"Gerando gift card {i+1}/{quantidade}")
        tentativas = 0
        while True:
            tentativas += 1
            codigo = random.choices(string.ascii_uppercase + string.digits, k=9)
            codigo = ''.join(codigo)
            print(f"Tentativa {tentativas}: Código gerado: {codigo}")
            
            try:
                validacao = api.GiftCard.validar_gift(codigo)
                print(f"Validação do código {codigo}: {validacao}")
                
                if validacao[0] == False:
                    print(f"Código {codigo} é válido, criando gift card...")
                    api.GiftCard.create_gift(codigo, float(valor))
                    codigos += f'\n{codigo}'
                    print(f"Gift card {codigo} criado com sucesso!")
                    break
                else:
                    print(f"Código {codigo} já existe, tentando novamente...")
                    if tentativas > 10:
                        print(f"Muitas tentativas para o gift {i+1}, pulando...")
                        break
            except Exception as e:
                print(f"Erro ao validar/criar gift card: {e}")
                print(f"Tipo de erro: {type(e).__name__}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                break
    print(f"Códigos finais gerados: {codigos}")
    print("=== FIM DEBUG GERAR MUITO GIFT ===")
    return codigos

def gerar_gift_card(valor):
    print(f"=== DEBUG GERAR GIFT CARD ===")
    print(f"Valor solicitado: {valor}")
    tentativas = 0
    while True:
        tentativas += 1
        codigo = random.choices(string.ascii_uppercase + string.digits, k=9)
        codigo = ''.join(codigo)
        print(f"Tentativa {tentativas}: Código gerado: {codigo}")
        
        try:
            validacao = api.GiftCard.validar_gift(codigo)
            print(f"Validação do código {codigo}: {validacao}")
            
            if validacao[0] == False:
                print(f"Código {codigo} é válido, criando gift card...")
                api.GiftCard.create_gift(codigo, float(valor))
                print(f"Gift card {codigo} criado com sucesso!")
                break
            else:
                print(f"Código {codigo} já existe, tentando novamente...")
                if tentativas > 10:
                    print(f"Muitas tentativas, usando código existente...")
                    break
        except Exception as e:
            print(f"Erro ao validar/criar gift card: {e}")
            print(f"Tipo de erro: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            break
    
    resultado = f'R${int(valor)},00', codigo
    print(f"Resultado final: {resultado}")
    print("=== FIM DEBUG GERAR GIFT CARD ===")
    return resultado

@bot.message_handler(commands=['resgatar'])
def redeem_gift(message):
    msg = message.text.strip().split()
    if len(msg) != 2:
        bot.reply_to(message, "Erro, envie no formato correto.\nex: /resgatar 1isjue")
        return
    codigo = msg[1]
    processar_resgate(message.chat.id, codigo)

def processar_resgate(id, codigo):
    verif, valor = api.GiftCard.validar_gift(codigo)
    if verif == True:
        api.GiftCard.del_gift(codigo)
        api.MudancaHistorico.mudar_gift_resgatado(id, float(valor))
        api.InfoUser.add_saldo(id, valor)
        bot.send_message(int(id), f'🎉 <b>Parabéns!</b>\nVocê resgatou o Gift Card com sucesso ✅\n\n💰 <b>Valor:</b> {valor:.2f}\n📔 <b>Código: </b>{codigo}', parse_mode='HTML')
        bot.send_message(int(api.CredentialsChange.id_dono()), f'⚠️ <b>GIFT CARD RESGATADO</b> 🙋\nUsuario: {id} acabou de resgatar o gift card: {codigo} e obteve um saldo de R${valor:.2f}', parse_mode='HTML')
        
        try:
            afiliado_por = api.InfoUser.pegar_afiliado_por(id)
            if afiliado_por and afiliado_por != 0:
                porcentagem = api.AfiliadosInfo.porcentagem_por_indicacao()
                valor_ganho = float(valor) * int(porcentagem) / 100
                
                api.InfoUser.add_saldo(int(afiliado_por), valor_ganho)
                
                try:
                    user_info = bot.get_chat(int(id))
                    indicado_nome = user_info.first_name if user_info.first_name else "Usuário"
                    indicado_username = f"@{user_info.username}" if user_info.username else "Sem username"
                except:
                    indicado_nome = "Usuário"
                    indicado_username = "Sem username"
                
                texto_notificacao_gift = (
                    f"🎁 <b>SEU INDICADO RESGATOU UM GIFT CARD!</b>\n\n"
                    f"👤 <b>Indicado:</b> {indicado_nome}\n"
                    f"🆔 <b>ID:</b> <code>{id}</code>\n"
                    f"📱 <b>Username:</b> {indicado_username}\n\n"
                    f"💵 <b>Valor do gift:</b> R${float(valor):.2f}\n"
                    f"🎁 <b>Você ganhou:</b> R${valor_ganho:.2f} ({porcentagem}%)\n\n"
                    f"✅ <b>O valor já foi creditado no seu saldo!</b>"
                )
                
                bot.send_message(int(afiliado_por), texto_notificacao_gift, parse_mode='HTML')
                print(f"✅ [NOTIFICAÇÃO GIFT] Indicador {afiliado_por} notificado sobre gift resgatado por {id}")
        except Exception as e:
            print(f"⚠️ [NOTIFICAÇÃO GIFT] Erro ao notificar indicador: {e}")
    else:
        bot.send_message(id, "Gift card invalido ou ja resgatado!")
        return

@bot.message_handler(commands=['start','menu', f'start@{api.CredentialsChange.user_bot()}'])
def handle_start(message):
    print("=" * 80)
    print(f"[START DEBUG] ⚡ COMANDO /START RECEBIDO!")
    print(f"[START DEBUG] 👤 User ID: {message.from_user.id}")
    print(f"[START DEBUG] 📝 Username: @{message.from_user.username if message.from_user.username else 'sem_username'}")
    print(f"[START DEBUG] 💬 Texto completo: '{message.text}'")
    print(f"[START DEBUG] 📊 Tipo de mensagem: {type(message.text)}")
    print(f"[START DEBUG] 📏 Tamanho do texto: {len(message.text)} caracteres")
    print("=" * 80)
    
    usuario_existe = api.InfoUser.verificar_usuario(message.from_user.id)
    print(f"[START DEBUG] Usuário já existe no banco? {usuario_existe}")
    
    if not usuario_existe:
        print(f"[START DEBUG] ✅ Novo usuário detectado! Iniciando processo de registro...")
        api.InfoUser.novo_usuario(message.from_user.id)
        print(f"[START DEBUG] Usuário {message.from_user.id} adicionado ao banco de dados")
        
        print("=" * 80)
        print(f"[INDICAÇÃO DEBUG] 🔍 INICIANDO ANÁLISE DE CÓDIGO DE INDICAÇÃO")
        print(f"[INDICAÇÃO DEBUG] Texto original: '{message.text}'")
        
        partes_comando = message.text.split()
        print(f"[INDICAÇÃO DEBUG] Partes após split(): {partes_comando}")
        print(f"[INDICAÇÃO DEBUG] Quantidade de partes: {len(partes_comando)}")
        
        for i, parte in enumerate(partes_comando):
            print(f"[INDICAÇÃO DEBUG]   Parte {i}: '{parte}' (tipo: {type(parte)}, tamanho: {len(parte)})")
        print("=" * 80)
        
        if len(partes_comando) == 2:
            codigo_indicacao = partes_comando[1]
            print(f"[INDICAÇÃO DEBUG] Código detectado: '{codigo_indicacao}'")
            print(f"[INDICAÇÃO DEBUG] É dígito? {codigo_indicacao.isdigit()}")
            print(f"[INDICAÇÃO DEBUG] É diferente do próprio ID? {codigo_indicacao != str(message.from_user.id)}")
            
            if codigo_indicacao.isdigit() and codigo_indicacao != str(message.from_user.id):
                indicador_id = codigo_indicacao
                print(f"[INDICAÇÃO DEBUG] ✅ Código de afiliado VÁLIDO detectado: {indicador_id}")
                print(f"[INDICAÇÃO DEBUG] Registrando {message.from_user.id} como indicado de {indicador_id}")
                api.InfoUser.novo_afiliado(message.from_user.id, indicador_id)
                print(f"[INDICAÇÃO DEBUG] ✅ Indicação registrada com sucesso!")
                
                try:
                    novo_usuario_nome = message.from_user.first_name if message.from_user.first_name else "Usuário"
                    novo_usuario_username = f"@{message.from_user.username}" if message.from_user.username else "Sem username"
                    
                    total_indicados = api.InfoUser.quantidade_afiliados(int(indicador_id))
                    print(f"[INDICAÇÃO DEBUG] Total de indicados do indicador {indicador_id}: {total_indicados}")
                    
                    texto_notificacao = (
                        f"🎉 <b>NOVO INDICADO!</b>\n\n"
                        f"👤 <b>Nome:</b> {novo_usuario_nome}\n"
                        f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n"
                        f"📱 <b>Username:</b> {novo_usuario_username}\n\n"
                        f"👥 <b>Total de indicados:</b> {total_indicados}\n\n"
                        f"💡 <b>Lembre-se:</b> Você ganhará 10% quando ele fizer uma recarga!"
                    )
                    
                    safe_send_message(int(indicador_id), texto_notificacao, parse_mode='HTML')
                    print(f"✅ [NOTIFICAÇÃO INDICAÇÃO] Indicador {indicador_id} notificado sobre novo indicado {message.from_user.id}")
                except Exception as e:
                    print(f"⚠️ [NOTIFICAÇÃO INDICAÇÃO] Erro ao notificar indicador: {e}")
            else:
                if not codigo_indicacao.isdigit():
                    print(f"[INDICAÇÃO DEBUG] ❌ Código ignorado: não é um número válido")
                else:
                    print(f"[INDICAÇÃO DEBUG] ❌ Código ignorado: é o próprio ID do usuário")
        else:
            print(f"[INDICAÇÃO DEBUG] ℹ️ Nenhum código de indicação detectado (comando sem parâmetros)")
        
        try:
            print(f"[LOG REGISTRO] Iniciando envio de log de novo registro...")
            mensagem_log = api.Log.log_registro(message)
            print(f"[LOG REGISTRO] Mensagem gerada (primeiros 100 chars): {mensagem_log[:100]}...")
            enviar_log_multiplos_destinos(mensagem_log, 'log-registro')
        except Exception as e:
            print(f"[LOG REGISTRO] ❌ Erro ao enviar log de registro: {e}")
            import traceback
            print(f"[LOG REGISTRO] Traceback completo:\n{traceback.format_exc()}")
        
        bonus = float(api.CredentialsChange.BonusRegistro.bonus())
        api.InfoUser.add_saldo(message.from_user.id, bonus)
        print(f"[START DEBUG] Bônus de R${bonus:.2f} adicionado ao usuário {message.from_user.id}")
    else:
        print(f"[START DEBUG] ℹ️ Usuário {message.from_user.id} já existe no banco. Pulando registro e log.")
        print("=" * 80)
        print(f"[INDICAÇÃO DEBUG] ⚠️ USUÁRIO JÁ EXISTE - VERIFICANDO SE HÁ CÓDIGO DE INDICAÇÃO")
        print(f"[INDICAÇÃO DEBUG] Texto original: '{message.text}'")
        
        partes_comando = message.text.split()
        print(f"[INDICAÇÃO DEBUG] Partes após split(): {partes_comando}")
        print(f"[INDICAÇÃO DEBUG] Quantidade de partes: {len(partes_comando)}")
        
        if len(partes_comando) == 2:
            codigo_indicacao = partes_comando[1]
            print(f"[INDICAÇÃO DEBUG] ⚠️ Código detectado mas usuário já existe: '{codigo_indicacao}'")
            print(f"[INDICAÇÃO DEBUG] ⚠️ Indicação NÃO será registrada (usuário já cadastrado)")
        else:
            print(f"[INDICAÇÃO DEBUG] ℹ️ Nenhum código de indicação no comando")
        print("=" * 80)
    
    is_admin = api.Admin.verificar_admin(message.from_user.id) or api.CredentialsChange.id_dono() == int(message.from_user.id)
    
    print(f"[VERIFICAÇÃO CANAL START] Usuário {message.from_user.id}, é admin? {is_admin}")
    print(f"[VERIFICAÇÃO CANAL START] Status verificação ativado? {api.CredentialsChange.VerificacaoCanal.status_verificacao()}")
    
    if api.CredentialsChange.VerificacaoCanal.status_verificacao() and not is_admin:
        print(f"[VERIFICAÇÃO CANAL START] Iniciando verificação para usuário {message.from_user.id}")
        
        eh_membro = api.CredentialsChange.VerificacaoCanal.verificar_membro_canal(message.from_user.id, api.CredentialsChange.token_bot())
        print(f"[VERIFICAÇÃO CANAL START] Resultado: eh_membro = {eh_membro}")
        
        if not eh_membro:
            print(f"[VERIFICAÇÃO CANAL START] ❌ Usuário {message.from_user.id} NÃO é membro - bloqueando acesso (mas indicação já foi registrada)")
            link_canal = api.CredentialsChange.VerificacaoCanal.link_canal()
            if not link_canal:
                link_canal = "https://t.me/meucanal"
            
            texto_verificacao = api.Textos.verificacao_canal(message, link_canal)
            
            bt_entrar = InlineKeyboardButton('🔗 ENTRAR NO CANAL', url=link_canal)
            bt_verificar_novamente = InlineKeyboardButton('🔄 VERIFICAR NOVAMENTE', callback_data='verificar_canal')
            
            markup = InlineKeyboardMarkup([[bt_entrar], [bt_verificar_novamente]])
            
            bot.send_message(message.chat.id, texto_verificacao, parse_mode='HTML', reply_markup=markup)
            return
        else:
            print(f"[VERIFICAÇÃO CANAL START] ✅ Usuário {message.from_user.id} É membro - permitindo acesso")
            
            if api.CredentialsChange.VerificacaoCanal.status_notificacao():
                try:
                    admin_id = api.CredentialsChange.id_dono()
                    user_name = message.from_user.first_name if hasattr(message.from_user, 'first_name') else 'Usuário'
                    user_username = message.from_user.username if hasattr(message.from_user, 'username') else 'Sem username'
                    user_id = message.from_user.id
                    
                    if not usuario_existe:
                        notification_text = f"🎉 <b>NOVO USUÁRIO ENTROU NO CANAL!</b>\n\n👤 <b>Nome:</b> {user_name}\n🆔 <b>ID:</b> {user_id}\n📱 <b>Username:</b> @{user_username}\n\n✅ <b>Status:</b> Verificação de canal aprovada\n🔗 <b>Ação:</b> Acessou o bot pela primeira vez"
                    else:
                        notification_text = f"🔄 <b>USUÁRIO REENTROU NO CANAL!</b>\n\n👤 <b>Nome:</b> {user_name}\n🆔 <b>ID:</b> {user_id}\n📱 <b>Username:</b> @{user_username}\n\n✅ <b>Status:</b> Verificação de canal aprovada\n🔗 <b>Ação:</b> Reacessou o bot"
                    
                    print(f"[VERIFICAÇÃO CANAL START] Notificando admin sobre usuário {user_id}")
                    bot.send_message(admin_id, notification_text, parse_mode='HTML')
                except Exception as e:
                    print(f"[VERIFICAÇÃO CANAL START] Erro ao notificar admin: {e}")
    else:
        if not api.CredentialsChange.VerificacaoCanal.status_verificacao():
            print(f"[VERIFICAÇÃO CANAL START] Verificação desativada - pulando validação")
        else:
            print(f"[VERIFICAÇÃO CANAL START] Usuário é admin - pulando validação")
    
    if api.InfoUser.verificar_ban(message.from_user.id) == True:
        partes_comando = message.text.split()
        print(f"[INDICAÇÃO DEBUG] Partes do comando: {partes_comando}")
        print(f"[INDICAÇÃO DEBUG] Quantidade de partes: {len(partes_comando)}")
        
        if len(message.text.split()) == 2:
            codigo_indicacao = message.text.split()[1]
            print(f"[INDICAÇÃO DEBUG] Código detectado: '{codigo_indicacao}'")
            print(f"[INDICAÇÃO DEBUG] É dígito? {codigo_indicacao.isdigit()}")
            print(f"[INDICAÇÃO DEBUG] É diferente do próprio ID? {codigo_indicacao != str(message.from_user.id)}")
            
            if message.text.split()[1].isdigit():
                if message.text.split()[1] != str(message.from_user.id):
                    indicador_id = message.text.split()[1]
                    print(f"[INDICAÇÃO DEBUG] ✅ Código de afiliado VÁLIDO detectado: {indicador_id}")
                    print(f"[INDICAÇÃO DEBUG] Registrando {message.from_user.id} como indicado de {indicador_id}")
                    api.InfoUser.novo_afiliado(message.from_user.id, indicador_id)
                    print(f"[INDICAÇÃO DEBUG] ✅ Indicação registrada com sucesso!")
                    
                    try:
                        novo_usuario_nome = message.from_user.first_name if message.from_user.first_name else "Usuário"
                        novo_usuario_username = f"@{message.from_user.username}" if message.from_user.username else "Sem username"
                        
                        total_indicados = api.InfoUser.quantidade_afiliados(int(indicador_id))
                        print(f"[INDICAÇÃO DEBUG] Total de indicados do indicador {indicador_id}: {total_indicados}")
                        
                        texto_notificacao = (
                            f"🎉 <b>NOVO INDICADO!</b>\n\n"
                            f"👤 <b>Nome:</b> {novo_usuario_nome}\n"
                            f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n"
                            f"📱 <b>Username:</b> {novo_usuario_username}\n\n"
                            f"👥 <b>Total de indicados:</b> {total_indicados}\n\n"
                            f"💡 <b>Lembre-se:</b> Você ganhará 10% quando ele fizer uma recarga!"
                        )
                        
                        safe_send_message(int(indicador_id), texto_notificacao, parse_mode='HTML')
                        print(f"✅ [NOTIFICAÇÃO INDICAÇÃO] Indicador {indicador_id} notificado sobre novo indicado {message.from_user.id}")
                    except Exception as e:
                        print(f"⚠️ [NOTIFICAÇÃO INDICAÇÃO] Erro ao notificar indicador: {e}")
                else:
                    print(f"[INDICAÇÃO DEBUG] ❌ Código ignorado: é o próprio ID do usuário")
            else:
                print(f"[INDICAÇÃO DEBUG] ❌ Código ignorado: não é um número válido")
        else:
            print(f"[INDICAÇÃO DEBUG] ℹ️ Nenhum código de indicação detectado (comando sem parâmetros)")
        
        try:
            print(f"[LOG REGISTRO] Iniciando envio de log de novo registro...")
            mensagem_log = api.Log.log_registro(message)
            print(f"[LOG REGISTRO] Mensagem gerada (primeiros 100 chars): {mensagem_log[:100]}...")
            enviar_log_multiplos_destinos(mensagem_log, 'log-registro')
        except Exception as e:
            print(f"[LOG REGISTRO] ❌ Erro ao enviar log de registro: {e}")
            import traceback
            print(f"[LOG REGISTRO] Traceback completo:\n{traceback.format_exc()}")
        
        bonus = float(api.CredentialsChange.BonusRegistro.bonus())
        api.InfoUser.add_saldo(message.from_user.id, bonus)
        print(f"[START DEBUG] Bônus de R${bonus:.2f} adicionado ao usuário {message.from_user.id}")
    
    if api.InfoUser.verificar_ban(message.from_user.id) == True:
        if hasattr(message, 'message_id') and message.message_id != 0:
            bot.reply_to(message, "Você está banido neste bot e não pode utiliza-lo!")
        else:
            bot.send_message(message.chat.id, "Você está banido neste bot e não pode utiliza-lo!")
        return
    
    if api.CredentialsChange.status_manutencao() == True:
        if api.Admin.verificar_admin(message.from_user.id) == False:
            if api.CredentialsChange.id_dono() != int(message.from_user.id):
                if hasattr(message, 'message_id') and message.message_id != 0:
                    bot.reply_to(message, "O bot esta em manutenção, voltaremos em breve!")
                else:
                    bot.send_message(message.chat.id, "O bot esta em manutenção, voltaremos em breve!")
                return
        if hasattr(message, 'message_id') and message.message_id != 0:
            bot.reply_to(message, "O bot está em manutenção, mas você foi identificado como administrador!")
        else:
            bot.send_message(message.chat.id, "O bot está em manutenção, mas você foi identificado como administrador!")
    
    texto = api.Textos.start(message)
    
    # Criar os botões corretamente com InlineKeyboardMarkup
    bt_servicos = InlineKeyboardButton(f'{api.Botoes.comprar()}', callback_data='servicos')
    bt_paises = InlineKeyboardButton(f'{api.Botoes.paises()}', callback_data='paises')
    bt_pesquisar = InlineKeyboardButton(f'{api.Botoes.pesquisar_numero()}', callback_data='pesquisar')
    bt_historico = InlineKeyboardButton('📝 Histórico', callback_data='historico_user')
    bt_favoritos = InlineKeyboardButton('⭐ Favoritos', callback_data='favoritos')
    bt_suporte = InlineKeyboardButton(f'{api.Botoes.suporte()}', url=f'{api.CredentialsChange.SuporteInfo.link_suporte()}')
    bt_add_saldo = InlineKeyboardButton(f'{api.Botoes.addsaldo()}', callback_data='addsaldo')
    bt_ranking = InlineKeyboardButton('🏆 Ranking', callback_data='ranking_sms')
    bt_afiliados = InlineKeyboardButton('👥 Afiliados', callback_data='afiliados')
    bt_perfil = InlineKeyboardButton(f'{api.Botoes.perfil()}', callback_data='perfil')
    
    # Construir o markup com as linhas corretas
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(bt_servicos, bt_paises)
    markup.add(bt_pesquisar)
    markup.add(bt_favoritos, bt_historico)
    markup.add(bt_suporte)
    markup.add(bt_add_saldo)
    markup.add(bt_ranking, bt_afiliados)
    markup.add(bt_perfil)
    
    foto = api.CredentialsChange.FotoMenu.foto_atual()
    
    if foto.startswith('AgAC') or foto.startswith('BQAC') or foto.startswith('CAAC'):
        safe_send_photo(message.chat.id, foto, caption=texto, parse_mode='HTML', reply_markup=markup, reply_to_message_id=message.message_id)
    else:
        safe_send_photo(message.chat.id, open(foto, 'rb'), caption=texto, parse_mode='HTML', reply_markup=markup, reply_to_message_id=message.message_id)
        
@bot.message_handler(func=lambda message: message.text in ['👤 Perfil'])
def perfil(message):
    markup = InlineKeyboardMarkup()
    if api.AfiliadosInfo.status_afiliado() == True:
        bt2 = InlineKeyboardButton(f'{api.Botoes.trocar_pontos_por_saldo()}', callback_data=f'trocar_pontos')
        markup.add(bt2)
    bt3 = InlineKeyboardButton(f'{api.Botoes.voltar()}', callback_data='menu_start')
    markup.add(bt3)
    texto = api.Textos.perfil(message)
    if message.text == '/perfil' or message.text=='👤 Perfil':
        safe_send_message(chat_id=message.chat.id, text=texto, parse_mode='HTML', reply_markup=markup, reply_to_message_id=message.message_id)
    else:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            print(f"🗑️ [PERFIL] Mensagem deletada com sucesso para usuário {message.chat.id}")
        except Exception as e:
            print(f"⚠️ [PERFIL] Mensagem já foi deletada ou não pode ser deletada: {e}")
        safe_send_message(chat_id=message.chat.id, text=texto, parse_mode='HTML', reply_markup=markup, reply_to_message_id=message.message_id)

@bot.message_handler(func=lambda message: message.text in ['/servicos', '🔥 Serviços'])
def servicos(message):
    pais = api.InfoUser.pegar_pais_atual(message.chat.id)
    todos_servicos = api.InfoApi.servicos(pais)
    
    servicos_destaque = api.ServicosDestaque.obter_servicos_destaque()
    
    servicos_em_destaque = []
    servicos_normais = []
    
    try:
        with open('settings/traducoes_servicos.json', 'r', encoding='utf-8') as f:
            traducoes_data = json.load(f)
        traducoes = traducoes_data.get("traducoes", {})
    except:
        traducoes = {}
    
    for servico in todos_servicos:
        if str(servico["id"]) in servicos_destaque:
            servicos_em_destaque.append(servico)
        else:
            servicos_normais.append(servico)
    
    servicos_em_destaque_ordenados = []
    for codigo_destaque in servicos_destaque:
        for servico in servicos_em_destaque:
            if str(servico["id"]) == codigo_destaque:
                servicos_em_destaque_ordenados.append(servico)
                break
    
    servicos_normais_ordenados = sorted(servicos_normais, key=lambda x: x["nome"])
    servicos_finais = servicos_em_destaque_ordenados + servicos_normais_ordenados
    
    mostrar_servicos(message, servicos_finais, 0)

def mostrar_servicos(message, servicos, pagina):
    chat_id = message.chat.id
    num_botoes_max = 30
    inicio = pagina * num_botoes_max
    fim = (pagina + 1) * num_botoes_max
    servicos_pagina = servicos[inicio:fim]

    favoritos_ids = set(api.InfoUser.favoritos(chat_id))
    
    pais = api.InfoUser.pegar_pais_atual(message.chat.id)
    pais_name = api.InfoApi.pegar_pais(pais)
    
    markup = InlineKeyboardMarkup()
    for i in range(0, len(servicos_pagina), 2):
        servico1 = servicos_pagina[i]
        id1 = servico1["id"]
        nome1 = servico1["nome"]
        valor1 = servico1["valor"]
        prefixo1 = '⭐ ' if str(id1) in favoritos_ids else ''
        bt1 = InlineKeyboardButton(f'{prefixo1}{nome1} R${float(valor1):.2f}', callback_data=f'exibir_servico {id1}')
        if i + 1 < len(servicos_pagina):
            servico2 = servicos_pagina[i + 1]
            id2 = servico2["id"]
            nome2 = servico2["nome"]
            valor2 = servico2["valor"]
            prefixo2 = '⭐ ' if str(id2) in favoritos_ids else ''
            bt2 = InlineKeyboardButton(f'{prefixo2}{nome2} R${float(valor2):.2f}', callback_data=f'exibir_servico {id2}')
            markup.row(bt1, bt2)
        else:
            markup.row(bt1)
    if pagina > 0:
        bt_anterior = InlineKeyboardButton('◀️ Página Anterior', callback_data=f'pagina_servicos {pagina - 1}')
        markup.row(bt_anterior)
    if len(servicos) > (pagina + 1) * num_botoes_max:
        bt_proxima = InlineKeyboardButton('▶️ Próxima Página', callback_data=f'pagina_servicos {pagina + 1}')
        markup.row(bt_proxima)
    if message.from_user.is_bot and message.photo == None:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=api.Textos.menu_comprar(message), reply_markup=markup, parse_mode='HTML')
        except Exception as e:
            safe_send_message(chat_id, api.Textos.menu_comprar(message), reply_markup=markup, parse_mode='HTML', reply_to_message_id=message.message_id)
    else:
        safe_send_message(chat_id, api.Textos.menu_comprar(message), reply_markup=markup, parse_mode='HTML', reply_to_message_id=message.message_id)

def _servicos_favoritos_usuario(user_id):
    favoritos_ids = api.InfoUser.favoritos(user_id)
    if not favoritos_ids:
        return []

    pais = api.InfoUser.pegar_pais_atual(user_id)
    servicos_disponiveis = api.InfoApi.servicos(pais)
    servicos_map = {str(servico["id"]): servico for servico in servicos_disponiveis}

    favoritos = []
    for fav_id in favoritos_ids:
        servico = servicos_map.get(str(fav_id))
        if servico:
            favoritos.append(servico)
    return favoritos

def mostrar_favoritos(message, servicos, pagina):
    chat_id = message.chat.id
    num_botoes_max = 30
    inicio = pagina * num_botoes_max
    fim = (pagina + 1) * num_botoes_max
    servicos_pagina = servicos[inicio:fim]

    markup = InlineKeyboardMarkup()
    for i in range(0, len(servicos_pagina), 2):
        servico1 = servicos_pagina[i]
        id1 = servico1["id"]
        nome1 = servico1["nome"]
        valor1 = servico1["valor"]
        bt1 = InlineKeyboardButton(f'⭐ {nome1} R${float(valor1):.2f}', callback_data=f'exibir_servico {id1}')
        if i + 1 < len(servicos_pagina):
            servico2 = servicos_pagina[i + 1]
            id2 = servico2["id"]
            nome2 = servico2["nome"]
            valor2 = servico2["valor"]
            bt2 = InlineKeyboardButton(f'⭐ {nome2} R${float(valor2):.2f}', callback_data=f'exibir_servico {id2}')
            markup.row(bt1, bt2)
        else:
            markup.row(bt1)

    if pagina > 0:
        markup.row(InlineKeyboardButton('◀️ Página Anterior', callback_data=f'pagina_favoritos {pagina - 1}'))
    if len(servicos) > (pagina + 1) * num_botoes_max:
        markup.row(InlineKeyboardButton('▶️ Próxima Página', callback_data=f'pagina_favoritos {pagina + 1}'))

    markup.row(InlineKeyboardButton('🔥 Ver serviços', callback_data='servicos'))
    markup.row(InlineKeyboardButton(f'{api.Botoes.voltar()}', callback_data='menu_start'))

    texto = '<b>⭐ Seus serviços favoritos</b>'
    if message.from_user.is_bot and message.photo == None:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=texto, reply_markup=markup, parse_mode='HTML')
        except Exception as e:
            safe_send_message(chat_id, texto, reply_markup=markup, parse_mode='HTML', reply_to_message_id=message.message_id)
    else:
        safe_send_message(chat_id, texto, reply_markup=markup, parse_mode='HTML', reply_to_message_id=message.message_id)

def favoritos_menu(message):
    favoritos = _servicos_favoritos_usuario(message.chat.id)
    if len(favoritos) == 0:
        texto = 'Você ainda não adicionou nenhum serviço aos favoritos. Abra a lista de serviços e toque em ⭐ para salvar seus favoritos.'
        markup = InlineKeyboardMarkup([[InlineKeyboardButton('🔥 Ver serviços', callback_data='servicos')], [InlineKeyboardButton(f'{api.Botoes.voltar()}', callback_data='menu_start')]])
        if message.from_user.is_bot and message.photo == None:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=texto, reply_markup=markup, parse_mode='HTML')
        else:
            safe_send_message(message.chat.id, texto, reply_markup=markup, parse_mode='HTML', reply_to_message_id=message.message_id)
        return

    mostrar_favoritos(message, favoritos, 0)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pagina_servicos'))
def callback_pagina_servicos(call):
    pais = api.InfoUser.pegar_pais_atual(call.message.chat.id)
    servicos_ordenados = sorted(api.InfoApi.servicos(pais), key=lambda x: x["nome"])
    pagina = int(call.data.split()[-1])
    mostrar_servicos(call.message, servicos_ordenados, pagina)

@bot.message_handler(func=lambda message: message.text in ['/alertas'])
def alertas(message):
    pais = api.InfoUser.pegar_pais_atual(message.chat.id)
    servicos = api.InfoApi.servicos(pais)
    estao_sem_estoque = []
    for servico in servicos:
        try:
            if servico["id"] != 'full':
                info_servico2 = api.sms.getPrices(servico["id"], pais)[f"{pais}"]
                info_servico1 = info_servico2[f"{servico['id']}"]
                estoque = info_servico1["count"]
                if str(estoque) == '0':
                    estao_sem_estoque.append(servico)
        except Exception as e:
            pass
    servicos_ordenados = sorted(estao_sem_estoque, key=lambda x: x["nome"])
    mostrar_alertas(message, estao_sem_estoque, 0)

def mostrar_alertas(message, servicos, pagina):
    chat_id = message.chat.id
    num_botoes_max = 98
    inicio = pagina * num_botoes_max
    fim = (pagina + 1) * num_botoes_max
    servicos_pagina = servicos[inicio:fim]
    markup = InlineKeyboardMarkup()
    for i in range(0, len(servicos_pagina), 2):
        servico1 = servicos_pagina[i]
        id1 = servico1["id"]
        nome1 = servico1["nome"]
        valor1 = servico1["valor"]
        bt1 = InlineKeyboardButton(f'{nome1}', callback_data=f'exibir_alerta {id1}')
        if i + 1 < len(servicos_pagina):
            servico2 = servicos_pagina[i + 1]
            id2 = servico2["id"]
            nome2 = servico2["nome"]
            valor2 = servico2["valor"]
            bt2 = InlineKeyboardButton(f'{nome2}', callback_data=f'exibir_alerta {id2}')
            markup.row(bt1, bt2)
        else:
            markup.row(bt1)
    if pagina > 0:
        bt_anterior = InlineKeyboardButton('◀️ Página Anterior', callback_data=f'pagina_alertas {pagina - 1}')
        markup.row(bt_anterior)
    if len(servicos) > (pagina + 1) * num_botoes_max:
        bt_proxima = InlineKeyboardButton('▶️ Próxima Página', callback_data=f'pagina_alertas {pagina + 1}')
        markup.row(bt_proxima)
    if message.from_user.is_bot and message.photo == None:
        bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text='<b>♻️ Selecione um serviço, o bot ira te alertar quando chegar números novos:</b>', reply_markup=markup, parse_mode='HTML')
    else:
        safe_send_message(chat_id, '<b>♻️ Selecione um serviço, o bot ira te alertar quando chegar números novos:</b>', reply_markup=markup, parse_mode='HTML', reply_to_message_id=message.message_id)

@bot.message_handler(func=lambda message: message.text in ['/comparativo'])
def handle_comparativo(message):
    pais = api.InfoUser.pegar_pais_atual(message.chat.id)
    servicos_ordenados = sorted(api.InfoApi.servicos(pais), key=lambda x: x["nome"])
    mostrar_comparativo(message, servicos_ordenados, 0)

def mostrar_comparativo(message, servicos, pagina):
    chat_id = message.chat.id
    num_botoes_max = 98
    inicio = pagina * num_botoes_max
    fim = (pagina + 1) * num_botoes_max
    servicos_pagina = servicos[inicio:fim]
    markup = InlineKeyboardMarkup()
    for i in range(0, len(servicos_pagina), 2):
        servico1 = servicos_pagina[i]
        id1 = servico1["id"]
        nome1 = servico1["nome"]
        valor1 = servico1["valor"]
        bt1 = InlineKeyboardButton(f'{nome1}', callback_data=f'exibir_comparativo {id1}')
        if i + 1 < len(servicos_pagina):
            servico2 = servicos_pagina[i + 1]
            id2 = servico2["id"]
            nome2 = servico2["nome"]
            valor2 = servico2["valor"]
            bt2 = InlineKeyboardButton(f'{nome2}', callback_data=f'exibir_comparativo {id2}')
            markup.row(bt1, bt2)
        else:
            markup.row(bt1)
    if pagina > 0:
        bt_anterior = InlineKeyboardButton('◀️ Página Anterior', callback_data=f'pagina_comparativo {pagina - 1}')
        markup.row(bt_anterior)
    if len(servicos) > (pagina + 1) * num_botoes_max:
        bt_proxima = InlineKeyboardButton('▶️ Próxima Página', callback_data=f'pagina_comparativo {pagina + 1}')
        markup.row(bt_proxima)
    if message.from_user.is_bot and message.photo == None:
        bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text='🌐 <b>Aqui você tem um comparativo dos países onde o seu serviço preferido é mais barato:</b>', reply_markup=markup, parse_mode='HTML')
    else:
        safe_send_message(chat_id, '<b>🌐 Aqui você tem um comparativo dos países onde o seu serviço preferido é mais barato:</b>', reply_markup=markup, parse_mode='HTML', reply_to_message_id=message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pagina_comparativo'))
def callback_pagina_comparativo(call):
    pais = api.InfoUser.pegar_pais_atual(call.message.chat.id)
    servicos_ordenados = sorted(api.InfoApi.servicos(pais), key=lambda x: x["nome"])    
    pagina = int(call.data.split()[-1])
    mostrar_comparativo(call.message, servicos_ordenados, pagina)

@bot.message_handler(commands=['reativar'])
def handle_reativar(message):
    acessos = api.InfoUser.verificar_acessos_ativos(message.chat.id)
    if len(acessos) == 0:
        texto = 'Você não tem nenhuma reativação disponível!'
        markup = None
    else:
        markup = InlineKeyboardMarkup()
        for acesso in acessos:
            id_servico = acesso["id-servico"]
            valor = acesso["valor"]
            servico = acesso["servico"]
            numero = acesso["numero"]
            id_ativacao = acesso["id_ativacao"]
            botao = InlineKeyboardButton(f'Reativar {servico}', callback_data=f'reativar {id_ativacao}')
            markup.row(botao)
        texto = 'Selecione o serviço que deseja reativar:'
    safe_send_message(message.chat.id, texto, reply_markup=markup, parse_mode='HTML', reply_to_message_id=message.message_id)

def pegar_informacoes_reativar(id_ativacao, id):
    with open('database/users.json', 'r') as f:
        data = json.load(f)
    for user in data["users"]:
        if str(user["id"]) == str(id):
            for compra in user["compras"]:
                if str(compra["id_ativacao"]) == str(id_ativacao):
                    return compra
                else:
                    pass

def exibir_opcoes_de_alertas(message, servico):
    pais = api.InfoUser.pegar_pais_atual(message.chat.id)
    nome_do_servico = api.InfoApi.pegar_servico(pais, servico)["nome"]
    status_alerta = api.Alertas.verificar_alerta(message.chat.id, servico)
    if status_alerta == True:
        status_alerta = '🟢 Sim'
    else:
        status_alerta = '🔴 Não'
    botao_ativar_alerta = InlineKeyboardButton(f'Receber aviso: {status_alerta}', callback_data=f'mudar_stts_aviso {message.chat.id} {servico}')
    botao_voltar = InlineKeyboardButton('🔙', callback_data='alertas')
    markup = InlineKeyboardMarkup([[botao_ativar_alerta], [botao_voltar]])
    texto = f'Essa funcionalidade serve para você ser notificado quando o serviço <b>{nome_do_servico}</b> estiver em estoque'
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)

def exibir_servico(message, servico):
    pais = api.InfoUser.pegar_pais_atual(message.chat.id)
    pais_name = api.InfoApi.pegar_pais(pais)
    
    data = api._ensure_sms_provider_migration()
    provider_config = str(data.get("sms_provider", "herosms")).strip().lower()
    
    if provider_config == "todos":
        clients = api.sms_clients_all()
        total_stock = 0
        melhor_preco = float('inf')
        nome = None
        provedores_com_estoque = []
        
        for client in clients:
            try:
                print(f"🔍 [EXIBIR_SERVICO] Verificando {client.provider}")
                info_servico = client.getPrices(servico, pais)
                if f"{pais}" in info_servico and f"{servico}" in info_servico[f"{pais}"]:
                    servico_info = info_servico[f"{pais}"][f"{servico}"]
                    count = int(servico_info.get("count", 0))
                    cost = float(servico_info.get("cost", 0))
                    
                    print(f"📊 [EXIBIR_SERVICO] {client.provider}: {count} unidades, ${cost}")
                    
                    if count > 0:
                        total_stock += count
                        provedores_com_estoque.append(f"{client.provider}({count})")
                        if cost < melhor_preco:
                            melhor_preco = cost
                    
                    if not nome:
                        nome = api.InfoApi.mudar_nomes_servicos(servico) or f"Serviço {servico}"
            except Exception as e:
                print(f"❌ [EXIBIR_SERVICO] Erro ao verificar estoque no {client.provider}: {e}")
                continue
        
        print(f"📋 [EXIBIR_SERVICO] Estoque total: {total_stock} | Provedores: {', '.join(provedores_com_estoque)}")
        
        if melhor_preco != float('inf'):
            valor_dolar = api.InfoApi.obter_cotacao_dolar()
            preco_real = melhor_preco * valor_dolar
            porcentagem_lucro = float(api.InfoApi.porcentagem_lucro())
            valor = float(preco_real) + (float(preco_real) * porcentagem_lucro / 100)
        else:
            ds = api.InfoApi.pegar_servico(pais, servico)
            nome = ds["nome"]
            valor = ds["valor"]
            total_stock = ds["count"]
    else:
        ds = api.InfoApi.pegar_servico(pais, servico)
        nome = ds["nome"]
        valor = ds["valor"]
        total_stock = ds["count"]

    favorito = api.InfoUser.is_favorito(message.chat.id, servico)
    fav_label = '⭐ Remover favorito' if favorito else '⭐ Favoritar'
    botao_favorito = InlineKeyboardButton(fav_label, callback_data=f'toggle_fav {servico}')

    print(f"=== LOG SERVIÇO SELECIONADO ===")
    print(f"Usuário: {message.chat.first_name} (ID: {message.chat.id})")
    print(f"País: {pais_name} (ID: {pais})")
    print(f"Serviço selecionado: {nome}")
    print(f"ID do serviço: {servico}")
    print(f"Valor: R${float(valor):.2f}")
    print(f"Estoque: {total_stock}")
    print(f"Modo provedor: {provider_config}")
    print("=" * 40)
    
    if provider_config == "todos":
        escolher_provedor_servico(message, servico, pais, pais_name, nome, valor, total_stock)
    else:
        texto = api.Textos.exibir_servico(message, nome, valor, pais_name, total_stock)
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception as e:
            print(f"Erro ao deletar mensagem em exibir_servico: {e}")
        if pais != '73':
            rows = [
                [InlineKeyboardButton('Receber SMS', callback_data=f'comprar {servico} all'), InlineKeyboardButton('Comparativo', callback_data=f'comparativo {servico}')],
                [InlineKeyboardButton('➕ Mais Preços', callback_data=f'ver_todos_precos {servico} {pais}')],
                [botao_favorito],
                [InlineKeyboardButton(f"{api.Botoes.voltar()}", callback_data='servicos')]
            ]
            markup = InlineKeyboardMarkup(rows)
        else:
            rows = [
                [InlineKeyboardButton('Receber SMS', callback_data=f'comprar {servico} all')],
                [InlineKeyboardButton('Operadoras', callback_data=f'exibir_operadora {servico}'), InlineKeyboardButton('Comparativo', callback_data=f'comparativo {servico}')],
                [InlineKeyboardButton('➕ Mais Preços', callback_data=f'ver_todos_precos {servico} {pais}')],
                [botao_favorito],
                [InlineKeyboardButton('🔙', callback_data='servicos')]
            ]
            markup = InlineKeyboardMarkup(rows)
        bot.send_message(chat_id=message.chat.id, text=texto, parse_mode='HTML', reply_markup=markup)

def escolher_provedor_servico(message, servico, pais, pais_name, nome, valor, count):
    print(f"🎯 [ESCOLHER_PROVEDOR] Iniciando seleção de provedor")
    print(f"   └─ Serviço: {servico}")
    print(f"   └─ País: {pais} ({pais_name})")
    print(f"   └─ Nome: {nome}")
    print(f"   └─ Valor: R${float(valor):.2f}")
    print(f"   └─ Estoque Total: {count}")
    
    texto = f"📱 <b>ESCOLHA O PROVEDOR</b>\n\n"
    texto += f"🎯 <b>Serviço:</b> {nome}\n"
    texto += f"🌍 <b>País:</b> {pais_name}\n"
    texto += f"📦 <b>Estoque Total:</b> {count}\n\n"
    texto += f"💡 <b>Selecione qual provedor deseja utilizar para este serviço:</b>\n\n"

    buttons = []
    clients = api.sms_clients_all()
    contador_provedor = 1

    favorito = api.InfoUser.is_favorito(message.chat.id, servico)
    fav_label = '⭐ Remover favorito' if favorito else '⭐ Favoritar'
    botao_favorito = InlineKeyboardButton(fav_label, callback_data=f'toggle_fav {servico}')

    print(f"🔍 [ESCOLHER_PROVEDOR] Verificando {len(clients)} provedores disponíveis")

    for client in clients:
        try:
            print(f"🔍 [VERIFICANDO PROVEDOR] {client.provider.upper()}")
            info_servico = client.getPrices(servico, pais)
            print(f"📊 [RESPOSTA {client.provider.upper()}] {info_servico}")
            
            if f"{pais}" in info_servico:
                servico_info = info_servico[f"{pais}"].get(f"{servico}", {})
                print(f"📋 [DADOS {client.provider.upper()}] {servico_info}")
                
                if "cost" in servico_info:
                    preco = float(servico_info["cost"])
                    estoque_provedor = servico_info.get("count", 0)
                    
                    print(f"💰 [PREÇO {client.provider.upper()}] ${preco} | Estoque: {estoque_provedor}")
                    
                    valor_dolar = api.InfoApi.obter_cotacao_dolar()
                    preco_real = preco * valor_dolar
                    porcentagem_lucro = float(api.InfoApi.porcentagem_lucro())
                    valor_com_lucro = float(preco_real) + (float(preco_real) * porcentagem_lucro / 100)

                    if estoque_provedor > 0:
                        status_estoque = f"({estoque_provedor} disponível)"
                        button_text = f'Provedor {contador_provedor} - R${valor_com_lucro:.2f} {status_estoque}'
                    else:
                        status_estoque = "(Sem estoque)"
                        button_text = f'Provedor {contador_provedor} - R${valor_com_lucro:.2f} {status_estoque}'

                    buttons.append(InlineKeyboardButton(
                        button_text,
                        callback_data=f'selecionar_provedor {servico} {client.provider}'
                    ))
                    print(f"✅ [PROVEDOR ADICIONADO] {client.provider} - Estoque: {estoque_provedor}")
                    contador_provedor += 1
                else:
                    print(f"❌ [PROVEDOR SEM CUSTO] {client.provider} - Serviço não disponível")
            else:
                print(f"❌ [PROVEDOR SEM PAÍS] {client.provider} - País {pais} não encontrado")
        except Exception as e:
            print(f"❌ [ERRO PROVEDOR] {client.provider}: {e}")
            continue

    print(f"📋 [ESCOLHER_PROVEDOR] {len(buttons)} provedores adicionados aos botões")

    if not buttons:
        texto += "❌ <b>Nenhum provedor tem este serviço disponível no momento.</b>"
        print(f"❌ [ESCOLHER_PROVEDOR] Nenhum provedor disponível")

    linhas_markup = []
    if buttons:
        linhas_markup.append(buttons)
    
    mais_precos_btn = InlineKeyboardButton(
        '➕ Mais Preços',
        callback_data=f'ver_todos_precos {servico} {pais}'
    )
    linhas_markup.append([mais_precos_btn])
    
    comparacao_btn = InlineKeyboardButton(
        '🏆 Comparação',
        callback_data=f'comparativo_especifico {servico}'
    )
    linhas_markup.append([comparacao_btn, botao_favorito])
    
    linhas_markup.append([InlineKeyboardButton('🔙 VOLTAR', callback_data='servicos')])
    markup = InlineKeyboardMarkup(linhas_markup)

    try:
        bot.delete_message(message.chat.id, message.message_id)
        print(f"🗑️ [ESCOLHER_PROVEDOR] Mensagem anterior deletada")
    except Exception as e:
        print(f"⚠️ [ESCOLHER_PROVEDOR] Erro ao deletar mensagem: {e}")
    
    bot.send_message(chat_id=message.chat.id, text=texto, parse_mode='HTML', reply_markup=markup)
    print(f"✅ [ESCOLHER_PROVEDOR] Mensagem de seleção enviada")

def mostrar_precos_de_um_provedor(message, servico, pais, provider):
    clients = api.sms_clients_all()
    client = next((c for c in clients if c.provider.lower() == provider.lower()), None)
    if not client:
        try:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text="❌ Provedor não encontrado.",
                parse_mode="HTML"
            )
        except:
            bot.send_message(message.chat.id, "❌ Provedor não encontrado.", parse_mode='HTML')
        return
    
    valor_dolar = api.InfoApi.obter_cotacao_dolar()
    porcentagem_lucro = float(api.InfoApi.porcentagem_lucro())
    provider_label = client.provider.capitalize() if client.provider.lower() not in ["herosms", "grizzly"] else ("Provedor 1" if client.provider.lower() == "herosms" else "Provedor 2")
    
    texto = f"<b>{provider_label}</b>\nEscolha um preço para comprar:\n"
    pool_buttons = []
    encontrou = False
    
    if provider_label == "Provedor 1" and hasattr(client, "getTopCountriesByServiceRank"):
        try:
            rank = client.getTopCountriesByServiceRank(servico, freePrice=True)
            pais_str = str(pais)
            for v in rank.values():
                if str(v.get("country")) != pais_str:
                    continue
                free_map = v.get("freePriceMap")
                if not isinstance(free_map, dict):
                    continue
                for preco_str, estoque in free_map.items():
                    try:
                        preco_usd = float(preco_str)
                        estoque = int(estoque)
                    except Exception:
                        continue
                    preco_real = preco_usd * valor_dolar
                    valor_final = preco_real * (1 + porcentagem_lucro / 100)
                    label = f"R${valor_final:.2f} | {estoque} un."
                    pool_buttons.append(InlineKeyboardButton(label, callback_data=f"comprar_pool {servico} {pais} {provider} {preco_usd}"))
                    encontrou = True
                break
        except Exception as e:
            print(f"Erro no getTopCountriesByServiceRank: {e}")
    else:
        info_servico = client.getPrices(servico, pais)
        pais_key = str(pais)
        serv_key = str(servico)
        if pais_key in info_servico and serv_key in info_servico[pais_key]:
            dados_servico = info_servico[pais_key][serv_key]
            if isinstance(dados_servico, dict) and "cost" in dados_servico:
                preco_usd = float(dados_servico.get("cost", 0))
                estoque = int(dados_servico.get("count", 0))
                preco_real = preco_usd * valor_dolar
                valor_final = preco_real * (1 + porcentagem_lucro / 100)
                label = f"R${valor_final:.2f} | {estoque} un."
                pool_buttons.append(InlineKeyboardButton(label, callback_data=f"comprar_pool {servico} {pais} {provider} {preco_usd}"))
                encontrou = True
            elif isinstance(dados_servico, dict):
                for operadora, dados in dados_servico.items():
                    if not isinstance(dados, dict):
                        continue
                    preco_usd = float(dados.get("cost", 0))
                    estoque = int(dados.get("count", 0))
                    preco_real = preco_usd * valor_dolar
                    valor_final = preco_real * (1 + porcentagem_lucro / 100)
                    label = f"{operadora}: R${valor_final:.2f} | {estoque} un."
                    pool_buttons.append(InlineKeyboardButton(label, callback_data=f"comprar_pool {servico} {pais} {provider} {preco_usd}"))
                    encontrou = True

    buttons = [pool_buttons[i:i+2] for i in range(0, len(pool_buttons), 2)]
    if not encontrou:
        texto += "\n❌ Nenhum preço disponível."
    buttons.append([InlineKeyboardButton("🔙 VOLTAR", callback_data=f"ver_todos_precos {servico} {pais}")])
    markup = InlineKeyboardMarkup(buttons)
    
    try:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=texto,
            parse_mode="HTML",
            reply_markup=markup
        )
    except Exception as e:
        print(f"[PRECOS PROVEDOR] Erro ao editar mensagem: {e}")
        bot.send_message(message.chat.id, texto, parse_mode='HTML', reply_markup=markup)

def exibir_operadora(message, servico):    
    txt = '🚩 <b>Selecione a operadora do número:</b>'
    markup = InlineKeyboardMarkup([[InlineKeyboardButton('⚫️ QUALQUER OPERADORA', callback_data=f'comprar {servico} all')], [InlineKeyboardButton('🟣 VIVO', callback_data=f'comprar {servico} vivo')], [InlineKeyboardButton('🔴 CLARO', callback_data=f'comprar {servico} claro')], [InlineKeyboardButton('🔵 TIM', callback_data=f'comprar {servico} tim')], [InlineKeyboardButton('🟡 OI', callback_data=f'comprar {servico} oi')], [InlineKeyboardButton(f'{api.Botoes.voltar()}', callback_data=f'exibir_servico {servico}')]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=txt, parse_mode='HTML', reply_markup=markup)

def comparativo_especifico(message, servico):
    import os
    import time
    
    cache_file = f'cache_comparativos/{servico}.json'
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            timestamp = cache_data.get('timestamp', 0)
            dados = cache_data.get('dados', {})
            nome_servico = dados.get('nome_servico', f'Serviço {servico}')
            paises_data = dados.get('paises', {})
            
            tempo_atual = time.time()
            tempo_desde_atualizacao = tempo_atual - timestamp
            tempo_para_proxima = max(0, 600 - tempo_desde_atualizacao)
            
            if tempo_desde_atualizacao < 60:
                tempo_str = "agora"
            elif tempo_desde_atualizacao < 3600:
                minutos = int(tempo_desde_atualizacao / 60)
                tempo_str = f"{minutos} min atrás"
            else:
                horas = int(tempo_desde_atualizacao / 3600)
                tempo_str = f"{horas}h atrás"
            
            if tempo_para_proxima <= 0:
                proxima_str = "em breve"
            elif tempo_para_proxima < 60:
                proxima_str = f"{int(tempo_para_proxima)}s"
            else:
                minutos = int(tempo_para_proxima / 60)
                segundos = int(tempo_para_proxima % 60)
                proxima_str = f"{minutos}m {segundos}s"
            
            paises_processados = []
            for pais_id, pais_info in paises_data.items():
                if pais_info and pais_info.get('nome') and pais_info.get('valor'):
                    porcentagem_lucro = float(api.InfoApi.porcentagem_lucro())
                    cotacao_dolar = api.InfoApi.obter_cotacao_dolar()
                    
                    preco_usd = float(pais_info['valor'])
                    preco_brl = preco_usd * cotacao_dolar
                    preco_com_lucro = preco_brl + (preco_brl * porcentagem_lucro / 100)
                    
                    paises_processados.append({
                        'nome': pais_info['nome'],
                        'preco': preco_com_lucro,
                        'id': pais_id
                    })
            
            paises_processados.sort(key=lambda x: x['preco'])
            top_10 = paises_processados[:10]
            
            if top_10:
                text = f'📊 <b>COMPARATIVO - {nome_servico}</b>\n'
                text += f'🏆 <b>TOP {len(top_10)} PAÍSES MAIS BARATOS</b>\n\n'
                
                for i, pais in enumerate(top_10, 1):
                    preco_formatado = f"R${pais['preco']:.2f}"
                    text += f'{i}. 🌍 {pais["nome"]} - {preco_formatado}\n'
                
                text += f'\n💡 Clique em um país para selecioná-lo e comprar'
                text += f'\n🕐 Última atualização: {tempo_str}'
                text += f'\n🔄 Próxima atualização: {proxima_str}'
                
                buttons = []
                for pais in top_10:
                    pais_nome = pais['nome']
                    pais_id = pais['id']
                    buttons.append([InlineKeyboardButton(f"🌍 {pais_nome}", callback_data=f'mudar_pais_comparativo {pais_id} {servico}')])
                
                buttons.append([InlineKeyboardButton("🔙 VOLTAR", callback_data=f'exibir_servico {servico}')])
                markup = InlineKeyboardMarkup(buttons)
                
                safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=text, parse_mode='HTML', reply_markup=markup)
                return
                
        except Exception as e:
            print(f"Erro ao carregar cache para {servico}: {e}")
    
    call = api.InfoApi.comparativo(servico)
    call = sorted(call, key=lambda x: x["valor"])[:10]
    foram = 1
    pais = api.InfoUser.pegar_pais_atual(message.chat.id)
    ds = api.InfoApi.pegar_servico(pais, servico)
    nome = ds["nome"]
    text = f'😉 Economize na compra, veja em até 10 países onde o serviço {nome} é mais barato:\n\n'
    primeiro_pais = None
    primeiro_pais_id = None
    for of in call:
        pais = of["pais"]
        valor = f'{float(of["valor"]):.2f}'
        id = of["id"]
        if foram == 1:
            primeiro_pais = pais
            primeiro_pais_id = id
            text += f'• O serviço {nome} é mais barato no país {pais}, custando R$ {valor}\n\n'
        else:
            text += f'°{foram} R$ {valor} - {pais}\n'
        foram += 1
    text += '\nVocê pode trocar o país dos números com /paises'
    text += '\n🕐 Dados atualizados em tempo real'
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"Definir: {primeiro_pais}", callback_data=f'mudar_pais_comparativo {primeiro_pais_id} {servico}')], [InlineKeyboardButton("🔙", callback_data=f'exibir_servico {servico}')]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=text, parse_mode='HTML', reply_markup=markup)

def alertar_saldo_baixo_api():
    while True:
        minimo = api.CronSaldoApi.saldo_minimo()
        saldo = api.CronSaldoApi.saldo_atual()["balance-real"]
        if api.CronSaldoApi.status_aviso() == True:
            if float(saldo) >= float(minimo):
                continue
            else:
                try:
                    bot.send_message(api.CronSaldoApi.destino_id(), f'<b>Aviso:</b> <i>Saldo da API baixo!!!</i>', parse_mode='HTML')
                except Exception as e:
                    print(e)
                    continue
        else:
            continue
        pausa = api.CronSaldoApi.tempo_aviso()
        time.sleep(int(pausa))

def exibir_comparativo_comando(message, servico):
    import os
    import time
    
    cache_file = f'cache_comparativos/{servico}.json'
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            timestamp = cache_data.get('timestamp', 0)
            dados = cache_data.get('dados', {})
            nome_servico = dados.get('nome_servico', f'Serviço {servico}')
            paises_data = dados.get('paises', {})
            
            tempo_atual = time.time()
            tempo_desde_atualizacao = tempo_atual - timestamp
            tempo_para_proxima = max(0, 600 - tempo_desde_atualizacao)
            
            if tempo_desde_atualizacao < 60:
                tempo_str = "agora"
            elif tempo_desde_atualizacao < 3600:
                minutos = int(tempo_desde_atualizacao / 60)
                tempo_str = f"{minutos} min atrás"
            else:
                horas = int(tempo_desde_atualizacao / 3600)
                tempo_str = f"{horas}h atrás"
            
            if tempo_para_proxima <= 0:
                proxima_str = "em breve"
            elif tempo_para_proxima < 60:
                proxima_str = f"{int(tempo_para_proxima)}s"
            else:
                minutos = int(tempo_para_proxima / 60)
                segundos = int(tempo_para_proxima % 60)
                proxima_str = f"{minutos}m {segundos}s"
            
            paises_processados = []
            for pais_id, pais_info in paises_data.items():
                if pais_info and pais_info.get('nome') and pais_info.get('valor'):
                    porcentagem_lucro = float(api.InfoApi.porcentagem_lucro())
                    cotacao_dolar = api.InfoApi.obter_cotacao_dolar()
                    
                    preco_usd = float(pais_info['valor'])
                    preco_brl = preco_usd * cotacao_dolar
                    preco_com_lucro = preco_brl + (preco_brl * porcentagem_lucro / 100)
                    
                    paises_processados.append({
                        'nome': pais_info['nome'],
                        'preco': preco_com_lucro,
                        'id': pais_id
                    })
            
            paises_processados.sort(key=lambda x: x['preco'])
            top_10 = paises_processados[:10]
            
            if top_10:
                text = f'📊 <b>COMPARATIVO - {nome_servico}</b>\n'
                text += f'🏆 <b>TOP {len(top_10)} PAÍSES MAIS BARATOS</b>\n\n'
                
                for i, pais in enumerate(top_10, 1):
                    preco_formatado = f"R${pais['preco']:.2f}"
                    text += f'{i}. 🌍 {pais["nome"]} - {preco_formatado}\n'
                
                text += f'\n💡 Clique em um país para selecioná-lo e comprar'
                text += f'\n🕐 Última atualização: {tempo_str}'
                text += f'\n🔄 Próxima atualização: {proxima_str}'
                text += f'\n🤖 Cache atualizado automaticamente a cada 10min'
                
                buttons = []
                for pais in top_10:
                    pais_nome = pais['nome']
                    pais_id = pais['id']
                    buttons.append([InlineKeyboardButton(f"🌍 {pais_nome}", callback_data=f'mudar_pais_comparativo_cmd {pais_id}')])
                
                buttons.append([InlineKeyboardButton("🔙", callback_data=f'handle_comparativo')])
                markup = InlineKeyboardMarkup(buttons)
                
                safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=text, parse_mode='HTML', reply_markup=markup)
                return
                
        except Exception as e:
            print(f"Erro ao carregar cache para {servico}: {e}")
    
    call = api.InfoApi.comparativo(servico)
    call = sorted(call, key=lambda x: x["valor"])[:10]
    foram = 1
    pais = api.InfoUser.pegar_pais_atual(message.chat.id)
    ds = api.InfoApi.pegar_servico(pais, servico)
    nome = ds["nome"]
    text = f'😉 Economize na compra, veja em até 10 países onde o serviço {nome} é mais barato:\n\n'
    primeiro_pais = None
    primeiro_pais_id = None
    for of in call:
        pais = of["pais"]
        valor = f'{float(of["valor"]):.2f}'
        id = of["id"]
        if foram == 1:
            primeiro_pais = pais
            primeiro_pais_id = id
            text += f'• O serviço {nome} é mais barato no país {pais}, custando R$ {valor}\n\n'
        else:
            text += f'°{foram} R$ {valor} - {pais}\n'
        foram += 1
    text += '\nVocê pode trocar o país dos números com /paises'
    text += '\n🕐 Dados atualizados em tempo real'
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"Definir: {primeiro_pais}", callback_data=f'mudar_pais_comparativo_cmd {primeiro_pais_id}')], [InlineKeyboardButton("🔙", callback_data=f'handle_comparativo')]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=text, parse_mode='HTML', reply_markup=markup)

def monitorar_ativacao(chat_id, id_ativacao, numero, operadora, servico, valor, provedor_forcado=None):
    """
    Monitora uma ativação para receber SMS e processa cancelamentos automáticos
    Versão ROBUSTA com suporte a múltiplos provedores
    """
    # DECLARAR GLOBAL LOGO NO INÍCIO DA FUNÇÃO
    global cancel_data
    
    print(f"=== INÍCIO monitorar_ativacao (ID:{id_ativacao}) ===")
    print(f"📱 [MONITOR] Dados recebidos:")
    print(f"   └─ Chat ID: {chat_id}")
    print(f"   └─ Ativação ID: {id_ativacao}")
    print(f"   └─ Número: {numero}")
    print(f"   └─ Operadora: {operadora}")
    print(f"   └─ Serviço: {servico}")
    print(f"   └─ Valor: R${float(valor):.2f}")
    print(f"   └─ Provedor Forçado: {provedor_forcado}")
    
    # Verificar se já foi processado
    if api.InfoUser.verificar_reembolso_duplicado(chat_id, id_ativacao):
        print(f"⚠️ [MONITOR] Ativação {id_ativacao} já foi processada - ENCERRANDO")
        return
    
    # ========== IDENTIFICAÇÃO ROBUSTA DO PROVEDOR ==========
    provedor_real = None
    
    # 1. Tentar usar o provedor_forcado
    if provedor_forcado:
        provedor_real = provedor_forcado
        print(f"✅ [MONITOR] Usando provedor forcado: {provedor_real}")
    
    # 2. Se não tem forcado, tentar do cache global
    if not provedor_real:
        if str(id_ativacao) in cancel_data:
            provedor_real = cancel_data[str(id_ativacao)].get('provedor')
            if provedor_real:
                print(f"✅ [MONITOR] Provedor encontrado no cache: {provedor_real}")
    
    # 3. Se ainda não tem, buscar no banco de dados
    if not provedor_real:
        provedor_real = identificar_provedor_ativacao(id_ativacao, chat_id)
        if provedor_real:
            print(f"✅ [MONITOR] Provedor encontrado no banco: {provedor_real}")
    
    # 4. Fallback final - tentar adivinhar pelo formato do ID
    if not provedor_real:
        if str(id_ativacao).isdigit() and len(str(id_ativacao)) > 8:
            provedor_real = "herosms"
            print(f"⚠️ [MONITOR] Usando fallback: ID numérico longo -> {provedor_real}")
        else:
            clients = api.sms_clients_all()
            for client in clients:
                try:
                    status = client.getStatus(id_ativacao)
                    if status is not False and status is not None:
                        provedor_real = client.provider
                        print(f"✅ [MONITOR] Provedor identificado por tentativa: {provedor_real}")
                        break
                except:
                    continue
        
        if not provedor_real:
            provedor_real = "herosms"
            print(f"⚠️ [MONITOR] Nenhum provedor identificado, usando padrão: {provedor_real}")
    
    print(f"✅ [MONITOR] Provedor final definido: {provedor_real}")
    
    # ========== VERIFICAÇÃO CRUZADA DO PROVEDOR ==========
    if provedor_real:
        try:
            status_teste = api.InfoApi.pegar_status_numero(id_ativacao, provedor=provedor_real)
            if status_teste is False or status_teste is None:
                print(f"⚠️ Provedor {provedor_real} não reconhece a ativação! Buscando em outros provedores...")
                status_real, provedor_real = verificar_status_em_todos_provedores(id_ativacao)
                if provedor_real:
                    print(f"✅ Provedor corrigido para: {provedor_real}")
        except Exception as e:
            print(f"⚠️ Erro na verificação cruzada: {e}")
            
    # ========== PREPARAR DADOS PARA EXIBIÇÃO ==========
    if numero and str(numero).startswith('55'):
        numero_sddi = str(numero)[2:]
        ddd = numero_sddi[:2]
        numero_local = numero_sddi[2:]
    else:
        numero_sddi = str(numero) if numero else ""
        ddd = "??"
        numero_local = numero_sddi
    
    operadora_display = operadora if operadora and operadora != 'None' else 'Qualquer operadora'
    
    if operadora_display != 'Qualquer operadora':
        operadora_display = operadora_display.capitalize()
    
    tempo_minutos = api.CredentialsChange.tempo_expiracao_sms()
    tempo_total_segundos = tempo_minutos * 60
    tempo_inicio = time.time()
    tempo_limite = tempo_inicio + tempo_total_segundos
    
    pais1 = api.InfoUser.pegar_pais_atual(chat_id)
    pais = api.InfoApi.pegar_pais(pais1) if pais1 else "Desconhecido"
    
    # ========== CONSTRUIR MENSAGEM INICIAL RICA (SEM PROVEDOR) ==========
    linha_separadora = "━━━━━━━━━━━━━━━━━━━━"
    
    txt = f"<b>✅ NÚMERO GERADO COM SUCESSO!</b>\n\n"
    txt += f"{linha_separadora}\n"
    txt += f"🌍 <b>País:</b> {pais}\n"
    txt += f"📱 <b>Serviço:</b> {servico}\n"
    txt += f"📶 <b>Operadora:</b> {operadora_display}\n"
    txt += f"{linha_separadora}\n\n"
    
    txt += f"📞 <b>Número completo:</b>\n"
    txt += f"<code>+{numero}</code>\n\n"
    
    txt += f"🔢 <b>Número (sem DDI):</b>\n"
    txt += f"<code>{numero_sddi}</code>\n\n"
    
    if ddd != "??":
        txt += f"📍 <b>DDD:</b> {ddd}\n"
        txt += f"📞 <b>Número local:</b> {numero_local}\n\n"
    
    txt += f"{linha_separadora}\n"
    txt += f"⏱️ <b>Tempo disponível:</b> {tempo_minutos} minutos\n"
    txt += f"💰 <b>Valor pago:</b> R${float(valor):.2f}\n"
    txt += f"{linha_separadora}\n\n"
    
    if servico and servico.lower() == 'telegram':
        txt += f"💡 <b>Dica para Telegram:</b>\n"
        txt += f"• Ative a verificação em duas etapas\n"
        txt += f"• Não compartilhe seu código com ninguém\n\n"
    elif servico and servico.lower() == 'whatsapp':
        txt += f"💡 <b>Dica para WhatsApp:</b>\n"
        txt += f"• O código chega em até 20 minutos\n"
        txt += f"• Se não receber, cancele e tente novamente\n\n"
    else:
        txt += f"💡 <b>Instruções:</b>\n"
        txt += f"• Use o número no aplicativo desejado\n"
        txt += f"• O código aparecerá automaticamente aqui\n\n"
    
    txt += f"<i>O número será automaticamente cancelado e o valor estornado após {tempo_minutos} minutos se nenhum SMS for recebido.</i>"
    
    cancel_data[str(id_ativacao)] = {
        'valor': valor,
        'numero': numero,
        'servico': servico,
        'provedor': provedor_real or 'herosms',
        'usuario': chat_id,
        'timestamp_geracao': time.time()
    }
    
    markup_cancelamento = InlineKeyboardMarkup([
        [InlineKeyboardButton('❌ CANCELAR E REEMBOLSAR', callback_data=f'ccl {id_ativacao} {valor} {numero} {servico}')],
        [InlineKeyboardButton('🔄 Gerar novo número', callback_data=f'gerar_novo {servico}')]
    ])
    
    try:
        msg = bot.send_message(chat_id, txt, parse_mode='HTML', reply_markup=markup_cancelamento)
        msg_id = msg.message_id
        api.MudancaHistorico.update_message_id_ultima_compra(chat_id, msg_id)
        print(f"📤 [MONITOR] Mensagem inicial enviada: {msg_id}")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        if not api.InfoUser.verificar_reembolso_duplicado(chat_id, id_ativacao):
            with saldo_operation_lock(chat_id):
                api.InfoUser.add_saldo(chat_id, float(valor))
                api.InfoUser.marcar_como_reembolsado(chat_id, id_ativacao)
        return
    
    # ========== LOOP DE MONITORAMENTO ==========
    codigo = ''
    sms_recebido = False
    ultima_atualizacao = 0
    primeira_vez = True
    iteracao = 0
    ultimo_status = None
    
    import re
    
    while time.time() < tempo_limite and not sms_recebido:
        iteracao += 1
        tempo_restante = int(tempo_limite - time.time())
        minutos_rest = tempo_restante // 60
        segundos_rest = tempo_restante % 60
        
        if api.InfoUser.verificar_reembolso_duplicado(chat_id, id_ativacao):
            print(f"⚠️ [MONITOR] Reembolso detectado durante loop - ENCERRANDO")
            return
        
        if iteracao % 3 == 0 or primeira_vez:
            try:
                status = api.InfoApi.pegar_status_numero(id_ativacao, provedor=provedor_real)
                
                if status != ultimo_status:
                    print(f"📊 [STATUS] ID:{id_ativacao} | Status: {repr(status)}")
                    ultimo_status = status
                
            except Exception as e:
                print(f"❌ Erro ao obter status: {e}")
                time.sleep(2)
                continue
            
            if status is False:
                print(f"❌ [CANCELAMENTO DETECTADO] ID:{id_ativacao}")
                break
            
            if status and isinstance(status, str):
                sms_detectado = False
                codigo_novo = None
                tipo_deteccao = ""
                
                if '<b>Novo código:</b>' in status:
                    sms_detectado = True
                    tipo_deteccao = "HTML"
                    match = re.search(r'<b>Novo código:</b> <code>(.*?)</code>', status)
                    if match:
                        codigo_novo = match.group(1)
                    else:
                        codigo_novo = status.replace('<b>Novo código:</b> <code>', '').replace('</code>', '')
                    
                    print(f"✅ [SMS RECEBIDO - HTML] ID:{id_ativacao} | Código: {codigo_novo}")
                
                elif 'SMS code:' in status or 'Código SMS:' in status:
                    sms_detectado = True
                    tipo_deteccao = "TEXTO"
                    match = re.search(r'(?:SMS code|Código SMS)[:\s]+([A-Z0-9]+)', status, re.IGNORECASE)
                    if match:
                        codigo_novo = match.group(1)
                    else:
                        numeros = re.findall(r'\d+', status)
                        if numeros:
                            codigo_novo = numeros[0]
                        else:
                            codigo_novo = status
                    
                    print(f"✅ [SMS RECEBIDO - TEXTO] ID:{id_ativacao} | Código: {codigo_novo}")
                
                elif re.match(r'^\d{4,8}$', status.strip()):
                    sms_detectado = True
                    tipo_deteccao = "NÚMERO"
                    codigo_novo = status.strip()
                    print(f"✅ [SMS RECEBIDO - NÚMERO] ID:{id_ativacao} | Código: {codigo_novo}")
                
                elif 'código' in status.lower() or 'code' in status.lower():
                    sms_detectado = True
                    tipo_deteccao = "TEXTO COM CÓDIGO"
                    numeros = re.findall(r'\d+', status)
                    if numeros:
                        codigo_novo = numeros[0]
                        print(f"✅ [SMS RECEBIDO - TEXTO COM CÓDIGO] ID:{id_ativacao} | Código: {codigo_novo}")
                    else:
                        codigo_novo = status
                        print(f"⚠️ [SMS RECEBIDO] ID:{id_ativacao} - Formato não reconhecido")
                
                if sms_detectado and codigo_novo and codigo_novo not in codigo:
                    if codigo:
                        codigo += f'\n{codigo_novo}'
                        codigos_list = codigo.split('\n')
                        print(f"📝 [MAIS CÓDIGOS] Total: {len(codigos_list)} códigos")
                    else:
                        codigo = codigo_novo
                        print(f"📝 [PRIMEIRO CÓDIGO] Recebido com sucesso")
                    
                    sms_recebido = True
                    
                    try:
                        if '\n' in codigo:
                            lista_codigos = codigo.split('\n')
                            texto_sucesso = (
                                f"<b>✅ SMS RECEBIDO COM SUCESSO!</b>\n\n"
                                f"{linha_separadora}\n"
                                f"📱 <b>Serviço:</b> {servico}\n"
                                f"📞 <b>Número:</b> <code>+{numero}</code>\n"
                                f"{linha_separadora}\n\n"
                                f"<b>📩 Códigos recebidos ({len(lista_codigos)}):</b>\n"
                            )
                            for i, cod in enumerate(lista_codigos, 1):
                                texto_sucesso += f"{i}. <code>{cod}</code>\n"
                        else:
                            texto_sucesso = (
                                f"<b>✅ SMS RECEBIDO COM SUCESSO!</b>\n\n"
                                f"{linha_separadora}\n"
                                f"📱 <b>Serviço:</b> {servico}\n"
                                f"📞 <b>Número:</b> <code>+{numero}</code>\n"
                                f"{linha_separadora}\n\n"
                                f"<b>🔑 Código de verificação:</b>\n"
                                f"<code>{codigo}</code>\n\n"
                            )
                        
                        if ddd != "??":
                            texto_sucesso += f"📍 <b>DDD:</b> {ddd}\n"
                        
                        texto_sucesso += f"⏱️ <b>Tempo restante:</b> {minutos_rest:02d}:{segundos_rest:02d}\n\n"
                        texto_sucesso += f"<i>O número continuará ativo por mais alguns minutos caso precise reenviar o código.</i>"
                        
                        markup_final = InlineKeyboardMarkup([
                            [InlineKeyboardButton('🔄 Gerar Novamente', callback_data=f'gerar_novo {servico}')],
                            [InlineKeyboardButton('🔥 Ver serviços', callback_data='servicos')],
                            [InlineKeyboardButton('🏠 Menu', callback_data='menu_start')]
                        ])
                        
                        bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=msg_id,
                            text=texto_sucesso,
                            parse_mode='HTML',
                            reply_markup=markup_final
                        )
                        
                        print(f"✅ [MENSAGEM FINAL] Código(s) mostrado(s) ao usuário")
                        
                        api.InfoUser.marcar_compra_como_concluida(chat_id, id_ativacao)
                        api.LimiteGeracao.reseta_tentativas(chat_id)
                        
                        try:
                            texto_log = api.Log.log_sms_recebido(chat_id, servico, numero, codigo, valor)
                            enviar_log_multiplos_destinos(texto_log, 'log-recebeu-sms')
                            print(f"📤 [LOG] Log de SMS recebido enviado")
                        except Exception as e:
                            print(f"⚠️ [LOG] Erro ao enviar log de SMS recebido: {e}")
                        
                        print(f"✅ Monitoramento finalizado com SMS recebido")
                        print(f"=== FIM monitorar_ativacao (SUCESSO) ===")
                        return
                        
                    except Exception as e:
                        print(f"⚠️ Erro ao atualizar mensagem final: {e}")
        
        if not sms_recebido and (time.time() - ultima_atualizacao > 5 or primeira_vez):
            primeira_vez = False
            try:
                barra_progresso = ""
                proporcao = 1 - (tempo_restante / tempo_total_segundos)
                blocos_cheios = int(proporcao * 10)
                blocos_vazios = 10 - blocos_cheios
                barra_progresso = "█" * blocos_cheios + "░" * blocos_vazios
                
                texto_atualizado = (
                    f"<b>⏳ AGUARDANDO SMS...</b>\n\n"
                    f"{linha_separadora}\n"
                    f"📱 <b>Serviço:</b> {servico}\n"
                    f"📞 <b>Número:</b> <code>+{numero}</code>\n"
                    f"{linha_separadora}\n\n"
                    f"<b>📩 Códigos recebidos:</b>\n"
                )
                
                if codigo:
                    if '\n' in codigo:
                        lista_codigos = codigo.split('\n')
                        for i, cod in enumerate(lista_codigos, 1):
                            texto_atualizado += f"{i}. <code>{cod}</code>\n"
                    else:
                        texto_atualizado += f"<code>{codigo}</code>\n"
                else:
                    texto_atualizado += f"<i>Nenhum código ainda</i>\n\n"
                
                texto_atualizado += f"\n{linha_separadora}\n"
                texto_atualizado += f"⏱️ <b>Tempo restante:</b> {minutos_rest:02d}:{segundos_rest:02d}\n"
                texto_atualizado += f"📊 <b>Progresso:</b> {barra_progresso}\n"
                texto_atualizado += f"{linha_separadora}\n\n"
                texto_atualizado += f"<i>O código aparecerá automaticamente aqui quando chegar.</i>"
                
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=msg_id,
                    text=texto_atualizado,
                    parse_mode='HTML',
                    reply_markup=markup_cancelamento
                )
                ultima_atualizacao = time.time()
            except Exception as e:
                if "message is not modified" not in str(e).lower():
                    print(f"Erro ao atualizar mensagem: {e}")
        
        time.sleep(1)
    
    if not sms_recebido and not api.InfoUser.verificar_reembolso_duplicado(chat_id, id_ativacao):
        print(f"=== CANCELAMENTO AUTOMÁTICO POR TIMEOUT ===")
        print(f"⏰ Tempo esgotado após {tempo_minutos} minutos")
        print(f"🆔 Ativação: {id_ativacao}")
        print(f"👤 Usuário: {chat_id}")
        print(f"💰 Valor: R${float(valor):.2f}")
        print(f"🏢 Provedor inicial: {provedor_real}")
        
        sucesso = False
        mensagem = ""
        provedor_que_funcionou = None
        
        provedores_tentar = []
        if provedor_real:
            provedores_tentar.append(provedor_real)
        
        if provedor_real == "herosms":
            provedores_tentar.append("grizzly")
        elif provedor_real == "grizzly":
            provedores_tentar.append("herosms")
        else:
            provedores_tentar = ["herosms", "grizzly"]
        
        print(f"🔄 Tentativas programadas: {provedores_tentar}")
        
        for tentativa_provedor in provedores_tentar:
            print(f"🔄 Tentando cancelar no provedor: {tentativa_provedor}")
            
            try:
                resultado = api.InfoApi.mudar_status_numero(id_ativacao, '8', tentativa_provedor)
                print(f"📤 [TENTATIVA {tentativa_provedor}] Resultado: {resultado}")
                
                if resultado == 'ACCESS_CANCEL' or (isinstance(resultado, str) and 'ACCESS_CANCEL' in resultado):
                    sucesso = True
                    provedor_que_funcionou = tentativa_provedor
                    print(f"✅ Cancelamento bem-sucedido no provedor: {tentativa_provedor}")
                    break
                elif resultado == 'BAD_STATUS':
                    print(f"⚠️ BAD_STATUS no provedor {tentativa_provedor} - tentando próximo")
                else:
                    print(f"⚠️ Resposta inesperada: {resultado}")
            except Exception as e:
                print(f"❌ Erro na tentativa {tentativa_provedor}: {e}")
                continue
        
        if sucesso:
            with saldo_operation_lock(chat_id):
                api.InfoUser.add_saldo(chat_id, float(valor))
                api.InfoUser.marcar_como_reembolsado(chat_id, id_ativacao)
                api.MudancaHistorico.add_reembolso(chat_id, id_ativacao, valor)
            
            print(f"✅ [REEMBOLSO] ID:{id_ativacao} | User:{chat_id} | Valor:{valor} | Provedor:{provedor_que_funcionou}")
            
            saldo_atual = api.InfoUser.saldo(chat_id)
            
            texto_estorno = (
                f"<b>⏰ TEMPO ESGOTADO!</b>\n\n"
                f"{linha_separadora}\n"
                f"📱 <b>Serviço:</b> {servico}\n"
                f"📞 <b>Número:</b> <code>+{numero}</code>\n"
                f"{linha_separadora}\n\n"
                f"❌ <b>Nenhum SMS foi recebido em {tempo_minutos} minutos</b>\n\n"
                f"💰 <b>Valor estornado:</b> R${float(valor):.2f}\n"
                f"💳 <b>Saldo atual:</b> R${saldo_atual:.2f}\n\n"
                f"🔄 <b>Você pode tentar novamente com outro número!</b>"
            )
            
            markup_estorno = InlineKeyboardMarkup([
                [InlineKeyboardButton('🔄 Tentar Novamente', callback_data=f'gerar_novamente {servico}')],
                [InlineKeyboardButton('🏠 Menu', callback_data='menu_start')]
            ])
            
            try:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=msg_id,
                    text=texto_estorno,
                    parse_mode='HTML',
                    reply_markup=markup_estorno
                )
                print(f"✅ [MENSAGEM] Mensagem de estorno atualizada")
            except Exception as e:
                print(f"⚠️ Erro ao atualizar mensagem de estorno: {e}")
            
            try:
                texto_log = api.Log.log_cancelamento_auto(chat_id, id_ativacao, servico, numero, valor, tempo_minutos)
                enviar_log_multiplos_destinos(texto_log, 'log-cancelou-sms')
                print(f"📤 [LOG] Log de cancelamento automático enviado")
            except Exception as e:
                print(f"⚠️ Erro ao enviar log de cancelamento: {e}")
        else:
            try:
                dono_id = api.CredentialsChange.id_dono()
                
                status_hero = None
                status_grizzly = None
                try:
                    status_hero = api.InfoApi.pegar_status_numero(id_ativacao, provedor="herosms")
                except:
                    pass
                try:
                    status_grizzly = api.InfoApi.pegar_status_numero(id_ativacao, provedor="grizzly")
                except:
                    pass
                
                erro_detalhado = (
                    f"Tentativas falharam em todos os provedores.\n"
                    f"Hero-SMS status: {status_hero}\n"
                    f"Grizzly status: {status_grizzly}"
                )
                
                bot.send_message(
                    dono_id,
                    f"🚨 <b>ERRO CRÍTICO</b>\n\n"
                    f"Não foi possível processar reembolso automático para ativação {id_ativacao}.\n\n"
                    f"👤 Usuário: {chat_id}\n"
                    f"💰 Valor: R${float(valor):.2f}\n"
                    f"❌ Detalhes: {erro_detalhado}\n"
                    f"🏢 Provedores tentados: {provedores_tentar}\n\n"
                    f"🔄 <b>Ação necessária:</b> Verificar manualmente!",
                    parse_mode='HTML'
                )
                print(f"📤 [ALERTA] Admin notificado sobre falha no reembolso")
            except Exception as e:
                print(f"❌ Erro ao notificar admin: {e}")
    
    print(f"=== FIM monitorar_ativacao ===")

def enviar_mensagem_bloqueio_com_countdown(user_id, servico_id, servico_nome, msg_erro, eh_inline=False, call=None):
    try:
        import threading
        
        tempo_atual = time.time()
        ultima_bloqueio = bloqueio_mensagens_cache.get(user_id, 0)
        
        if tempo_atual - ultima_bloqueio < BLOQUEIO_CACHE_TEMPO:
            print(f"⏱️ [BLOQUEIO] User {user_id} - Mensagem em cooldown (ignorada para evitar rate limit)")
            if eh_inline and call:
                try:
                    bot.answer_callback_query(call.id, "⏳ Bloqueio ativo. Aguarde...", show_alert=False)
                except:
                    pass
            return False
        
        bloqueio_mensagens_cache[user_id] = tempo_atual
        
        info = api.LimiteGeracao.obter_info_usuario(user_id)
        tempo_restante = info.get("tempo_restante_segundos", 0)
        
        if tempo_restante <= 0:
            return False
        
        markup = InlineKeyboardMarkup()
        botao_gerar = InlineKeyboardButton(
            f"⏳ Gerar Novamente ({tempo_restante}s)",
            callback_data=f"bloqueio_gerar_agora {servico_nome} {servico_id}"
        )
        markup.add(botao_gerar)
        
        msg_obj = bot.send_message(user_id, msg_erro, parse_mode='HTML', reply_markup=markup)
        
        if eh_inline and call:
            try:
                bot.answer_callback_query(call.id, "⏳ Bloqueio ativo. Aguarde...", show_alert=False)
            except:
                pass
        
        print(f"✅ [BLOQUEIO] Mensagem com countdown enviada para User {user_id} | {tempo_restante}s restante")
        
        def atualizar_countdown_inteligente():
            import time
            tempo_restante_local = tempo_restante
            
            while tempo_restante_local > 0:
                if tempo_restante_local > 300:
                    intervalo = 30
                elif tempo_restante_local > 120:
                    intervalo = 15
                elif tempo_restante_local > 60:
                    intervalo = 10
                else:
                    intervalo = 5
                
                time.sleep(intervalo)
                tempo_restante_local -= intervalo
                
                if tempo_restante_local < 0:
                    tempo_restante_local = 0
                
                try:
                    novo_botao = InlineKeyboardButton(
                        f"⏳ Gerar Novamente ({tempo_restante_local}s)" if tempo_restante_local > 0 else "✅ Gerar Novamente",
                        callback_data=f"bloqueio_gerar_agora {servico_nome} {servico_id}"
                    )
                    novo_markup = InlineKeyboardMarkup()
                    novo_markup.add(novo_botao)
                    
                    bot.edit_message_reply_markup(
                        chat_id=user_id,
                        message_id=msg_obj.message_id,
                        reply_markup=novo_markup
                    )
                    print(f"✅ [COUNTDOWN] User {user_id} ({servico_nome}): {tempo_restante_local}s restante")
                except Exception as e:
                    print(f"⚠️ [COUNTDOWN] Erro ao atualizar: {e}")
                    break
        
        thread = threading.Thread(target=atualizar_countdown_inteligente, daemon=True)
        thread.start()
        
        return True
    except Exception as e:
        print(f"❌ [BLOQUEIO] Erro ao enviar mensagem de bloqueio com countdown: {e}")
        return False

# ==================== FUNÇÃO entregar_inline ADICIONADA ====================
def entregar_inline(call, servico, operadora, valor):
    """Função para entregar números via inline query"""
    try:
        servico_id = servico
        if not api.InfoApi.tem_traducao(servico):
            servico_id = api.InfoApi.obter_id_servico(servico)
            if servico_id is None:
                print(f"❌ Serviço '{servico}' não tem ID mapping")
                safe_answer_callback(call, "❌ Serviço inválido.", show_alert=True)
                return
        
        if not api.sms_cooldown.can_request_sms(call.from_user.id, servico_id):
            remaining_time = api.sms_cooldown.get_remaining_time(call.from_user.id, servico_id)
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
            
            print(f"⏰ [COOLDOWN INLINE] User {call.from_user.id} - {time_str} de espera para {servico_id}")
            safe_answer_callback(call, f"⏰ Aguarde {time_str} para solicitar novamente.", show_alert=True)
            return
        
        pode_gerar, msg_erro = api.LimiteGeracao.pode_gerar(call.from_user.id, api.InfoUser.eh_constante)
        if not pode_gerar:
            enviar_mensagem_bloqueio_com_countdown(call.from_user.id, servico_id, servico, msg_erro, eh_inline=True, call=call)
            return
        
        api.LimiteGeracao.registrar_tentativa(call.from_user.id)
        
        pais = api.InfoUser.pegar_pais_atual(call.from_user.id)
        ds = api.InfoApi.pegar_servico(pais, servico_id)
        
        if ds is None:
            ds = api.InfoApi.pegar_servico(1, servico_id)
            if ds is None:
                safe_answer_callback(call, "❌ Serviço indisponível.", show_alert=True)
                return
            pais = 1
        
        info_number = api.InfoApi.comprar_numero(servico_id, pais, operadora)
        
        if isinstance(info_number, dict) and "error" in info_number:
            safe_answer_callback(call, f"❌ {info_number['error']}", show_alert=True)
            return
        elif info_number == False:
            safe_answer_callback(call, "❌ Sem estoque disponível.", show_alert=True)
            return
        
        api.sms_cooldown.add_cooldown(call.from_user.id, servico_id)
        
        numero = info_number["numero"]
        nome = ds["nome"]
        
        threading.Thread(
            target=monitorar_ativacao, 
            args=(
                call.from_user.id, 
                info_number["id"], 
                numero, 
                operadora, 
                nome, 
                valor,
                None
            )
        ).start()
        
        with saldo_operation_lock(call.from_user.id):
            api.InfoUser.tirar_saldo(call.from_user.id, float(valor))
        
        api.MudancaHistorico.add_compra(
            call.from_user.id, 
            servico, 
            valor, 
            numero, 
            nome, 
            info_number["id"], 
            info_number.get("provedor", "herosms"), 
            None
        )
        
        try:
            texto_adm = api.Log.log_compra(call.from_user.id, nome, numero, operadora, valor)
            bot_username = api.CredentialsChange.user_bot()
            bot_link = f"https://t.me/{bot_username}"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("📲 Abrir o bot", url=bot_link))
            enviar_log_multiplos_destinos(texto_adm, 'log-compra', reply_markup=markup)
        except Exception as e:
            print(f"[LOG COMPRA INLINE] ❌ Erro ao enviar log: {e}")
            
    except Exception as e:
        print(f"❌ ERRO em entregar_inline: {e}")
        import traceback
        traceback.print_exc()
        safe_answer_callback(call, "❌ Erro ao processar. Tente novamente.", show_alert=True)

# ==================== FUNÇÕES DE ENTREGA CORRIGIDAS ====================
def entregar_com_provedor(message, servico, operadora, valor, provedor_forcado=None, max_price=None, fixed_price=None, skip_saldo_deduction=False):
    print(f"🚀 [ENTREGAR_COM_PROVEDOR] Função chamada")
    print(f"   └─ Usuário: {message.chat.id}")
    print(f"   └─ Serviço: {servico}")
    print(f"   └─ Operadora: {operadora}")
    print(f"   └─ Valor: R${float(valor):.2f}")
    print(f"   └─ Provedor Forçado: {provedor_forcado}")
    print(f"   └─ Skip Saldo Deduction: {skip_saldo_deduction}")
    
    def get_provider_info(provedor_hint=None):
        try:
            provider_key = api.get_current_provider_name(provedor_hint).lower()
        except Exception:
            provider_key = "unknown"

        providers = {
            "herosms": {
                "display_name": "Hero-SMS",
                "url": "https://herosms.com/"
            },
            "grizzlysms": {
                "display_name": "GrizzlySMS",
                "url": "https://grizzlysms.com/"
            },
        }
        return providers.get(provider_key, {
            "display_name": provider_key or "SMS Provider",
            "url": ""
        })

    if max_price is not None:
        max_price = str(max_price)
    if fixed_price is not None:
        fixed_price = str(fixed_price)
    
    try:
        if not skip_saldo_deduction:
            saldo_usuario = float(api.InfoUser.saldo(message.chat.id))
            valor_float = float(valor)
            
            if saldo_usuario < valor_float - 0.001:
                print(f"❌ SALDO INSUFICIENTE: User {message.chat.id} | Saldo: R${saldo_usuario:.2f} | Valor: R${valor_float:.2f}")
                bot.send_message(
                    message.chat.id, 
                    f"❌ <b>SALDO INSUFICIENTE!</b>\n\n💰 <b>Seu saldo:</b> R${saldo_usuario:.2f}\n💵 <b>Valor necessário:</b> R${valor_float:.2f}\n\n👉 <b>Faça uma recarga para continuar.</b>", 
                    parse_mode='HTML'
                )
                return
        else:
            print(f"💳 [SKIP SALDO CHECK] Saldo já foi debitado anteriormente, pulando verificação")
        
        servico_id = servico
        if not api.InfoApi.tem_traducao(servico):
            servico_id = api.InfoApi.obter_id_servico(servico)
            if servico_id is None:
                print(f"❌ Serviço '{servico}' não tem ID mapping")
                bot.send_message(message.chat.id, "❌ Serviço inválido.", parse_mode='HTML')
                return
        
        if not api.sms_cooldown.can_request_sms(message.chat.id, servico_id):
            remaining_time = api.sms_cooldown.get_remaining_time(message.chat.id, servico_id)
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
            
            print(f"⏰ [COOLDOWN SERVIÇO] User {message.chat.id} - {time_str} de espera para {servico_id}")
            bot.send_message(
                message.chat.id, 
                f"⏰ <b>AGUARDE!</b>\n\nVocê solicitou um SMS deste serviço recentemente.\nAguarde <b>{time_str}</b> para solicitar novamente.", 
                parse_mode='HTML'
            )
            return
        
        pode_gerar, msg_erro = api.LimiteGeracao.pode_gerar(message.chat.id, api.InfoUser.eh_constante)
        if not pode_gerar:
            enviar_mensagem_bloqueio_com_countdown(message.chat.id, servico_id, servico, msg_erro, eh_inline=False)
            return
        
        api.LimiteGeracao.registrar_tentativa(message.chat.id)
        
        pais = api.InfoUser.pegar_pais_atual(message.chat.id)
        pais_name = api.InfoApi.pegar_pais(pais)
        ds = api.InfoApi.pegar_servico(pais, servico_id)
        
        if ds is None:
            print(f"[AVISO] pegar_servico retornou None para pais={pais}, servico_id={servico_id}")
            print(f"[TENTANDO] Fallback para país padrão 1 (Brasil)...")
            ds = api.InfoApi.pegar_servico(1, servico_id)
            if ds is None:
                print(f"[ERRO] Serviço não encontrado em nenhum país")
                bot.send_message(message.chat.id, "❌ Serviço indisponível no momento. Tente outro serviço ou país.", parse_mode='HTML')
                return
            pais = 1
            pais_name = api.InfoApi.pegar_pais(1)
            print(f"[SUCESSO] Serviço encontrado em país=1, usando como fallback")
        
        nome = ds["nome"]
        
        print(f"=== LOG TENTATIVA DE COMPRA ===")
        print(f"Usuário: {message.chat.first_name} (ID: {message.chat.id})")
        print(f"País: {pais_name} (ID: {pais})")
        print(f"Serviço: {nome} (ID: {servico_id})")
        print(f"Operadora: {operadora}")
        print(f"Valor: R${float(valor):.2f}")
        print("=" * 40)
        
        print(f"🔄 [COMPRAR_NUMERO] Chamando API")
        print(f"   └─ servico_id: {servico_id}")
        print(f"   └─ pais: {pais}")
        print(f"   └─ operadora: {operadora}")
        print(f"   └─ provedor_forcado: {provedor_forcado}")
        print(f"   └─ max_price: {max_price}")
        print(f"   └─ fixed_price: {fixed_price}")
        
        info_number = api.InfoApi.comprar_numero(
            servico_id,
            pais,
            operadora,
            provedor_forcado,
            max_price=max_price,
            fixed_price=fixed_price
        )

        print(f"🔍 [RESPOSTA API COMPRA] Tipo: {type(info_number)} | Conteúdo: {repr(info_number)}")
        
        if isinstance(info_number, dict) and "error" in info_number:
            error_type = info_number["error"]
            
            if skip_saldo_deduction:
                print(f"💰 [ESTORNO POOL] Erro detectado, estornando R${float(valor):.2f} para usuário {message.chat.id}")
                with saldo_operation_lock(message.chat.id):
                    api.InfoUser.add_saldo(message.chat.id, float(valor))
                novo_saldo = api.InfoUser.saldo(message.chat.id)
                print(f"💳 [ESTORNO CONCLUÍDO] Novo saldo: R${float(novo_saldo):.2f}")
            
            if error_type == "insufficient_balance":
                print(f"❌ FALHA: Saldo insuficiente na API do provedor para {nome}")
                
                dono_id = api.CredentialsChange.id_dono()
                provider_info = get_provider_info(provedor_forcado)
                
                try:
                    clients = api.sms_clients_all()
                    saldo_api_real = "$0.00"
                    for client in clients:
                        if client.provider.lower() == provedor_forcado.lower():
                            balance_info = client.getBalance()
                            if isinstance(balance_info, dict) and "balance" in balance_info:
                                saldo_api_real = f"${float(balance_info['balance']):.4f}"
                            break
                except Exception as e:
                    saldo_api_real = "$0.00"
                
                try:
                    bot.send_message(
                        dono_id, 
                        f"🚨 <b>ALERTA ADMINISTRADOR</b>\n\n❌ <b>Saldo insuficiente na API do {provider_info['display_name']}!</b>\n\n💰 <b>Saldo atual na API:</b> {saldo_api_real}\n👤 <b>Usuário afetado:</b> {message.chat.first_name} (ID: {message.chat.id})\n🌍 <b>Serviço:</b> {nome}\n🇺🇸 <b>País:</b> {pais_name}\n\n🔄 <b>Ação necessária:</b> Recarregue a conta", 
                        parse_mode='HTML'
                    )
                except Exception as e:
                    print(f"❌ Erro ao notificar dono: {e}")
                
                bot.send_message(
                    message.chat.id, 
                    f"⚠️ <b>Serviço temporariamente indisponível</b>\n\nTente novamente em alguns minutos.", 
                    parse_mode='HTML'
                )
            elif error_type == "no_stock":
                print(f"❌ FALHA: Sem estoque para {nome} no país {pais_name}")
                bot.send_message(
                    message.chat.id, 
                    f"Não temos estoque do serviço <b>{nome}</b> disponível.\nTente mais tarde ou verifique outros países...", 
                    parse_mode='HTML'
                )
            elif error_type == "no_stock_all_providers":
                print(f"❌ FALHA: Nenhum provedor tem estoque para {nome} no país {pais_name}")
                
                try:
                    dono_id = api.CredentialsChange.id_dono()
                    bot.send_message(
                        dono_id, 
                        f"🚨 <b>ALERTA ADMINISTRADOR</b>\n\n📦 <b>Sem estoque em TODOS os provedores!</b>\n\n👤 <b>Usuário:</b> {message.chat.first_name} (ID: {message.chat.id})\n🌍 <b>Serviço:</b> {nome}\n🇺🇸 <b>País:</b> {pais_name}\n\n⚠️ <b>Situação:</b> Todos os provedores configurados foram testados e nenhum conseguiu fornecer",
                        parse_mode='HTML'
                    )
                except Exception as e:
                    print(f"❌ Erro ao notificar admin: {e}")
                
                bot.send_message(
                    message.chat.id, 
                    f"⚠️ <b>Serviço temporariamente indisponível</b>\n\nNenhum provedor tem estoque de <b>{nome}</b> no momento.\n\nTente novamente em alguns minutos ou escolha outro país.", 
                    parse_mode='HTML'
                )
            elif error_type == "api_error":
                details = info_number.get("details", "Erro desconhecido")
                print(f"❌ FALHA: Erro da API - {details}")
                bot.send_message(
                    message.chat.id, 
                    f"Erro temporário na API. Tente novamente em alguns minutos.", 
                    parse_mode='HTML'
                )
            else:
                print(f"❌ FALHA: Erro desconhecido - {error_type}")
                bot.send_message(
                    message.chat.id, 
                    f"Erro inesperado. Entre em contato com o suporte.", 
                    parse_mode='HTML'
                )
            return
        elif info_number == False:
            if skip_saldo_deduction:
                print(f"💰 [ESTORNO POOL] Erro FALSE detectado, estornando R${float(valor):.2f} para usuário {message.chat.id}")
                with saldo_operation_lock(message.chat.id):
                    api.InfoUser.add_saldo(message.chat.id, float(valor))
            
            print(f"❌ FALHA: Sem estoque para {nome} no país {pais_name}")
            bot.send_message(
                message.chat.id, 
                f"Não temos estoque do serviço <b>{nome}</b> disponível.\nTente mais tarde ou verifique outros países...", 
                parse_mode='HTML'
            )
            return
        
        api.sms_cooldown.add_cooldown(message.chat.id, servico_id)
        
        numero = info_number["numero"]
        if operadora == None:
            operadora = 'Qualquer operadora'
        
        provedor_nome = api.get_current_provider_name(provedor_forcado)
        print(f"=== LOG NÚMERO GERADO ===")
        print(f"Usuário: {message.chat.first_name} (ID: {message.chat.id})")
        print(f"País: {pais_name} (ID: {pais})")
        print(f"Serviço: {nome} (ID: {servico})")
        print(f"Operadora: {operadora}")
        print(f"Provedor: {provedor_nome}")
        print(f"Número: +{numero}")
        print(f"ID da ativação: {info_number['id']}")
        print(f"Valor: R${float(valor):.2f}")
        print("=" * 40)
        
        print(f"=== INICIANDO THREAD monitorar_ativacao ===")
        print(f"ID que será passado: {info_number['id']}")
        print("=" * 50)
        
        threading.Thread(
            target=monitorar_ativacao, 
            args=(
                message.chat.id, 
                info_number["id"], 
                numero, 
                operadora, 
                nome, 
                valor, 
                provedor_forcado
            )
        ).start()
        
        if not skip_saldo_deduction:
            with saldo_operation_lock(message.chat.id):
                saldo_antes = api.InfoUser.saldo(message.chat.id)
                api.InfoUser.tirar_saldo(message.chat.id, float(valor))
                saldo_depois = api.InfoUser.saldo(message.chat.id)
            print(f"💸 [DEBITO NORMAL] User:{message.chat.id} | Ativacao:{info_number['id']} | Valor:{float(valor):.2f} | Antes:{saldo_antes:.2f} | Depois:{saldo_depois:.2f}")
        else:
            print(f"💸 [DEBITO PULADO] User:{message.chat.id} | Ativacao:{info_number['id']} | Valor:{float(valor):.2f} | Saldo já foi debitado no pool")

        provedor_para_registro = provedor_forcado or info_number.get("provedor", "herosms")

        api.MudancaHistorico.add_compra(
            message.chat.id, 
            servico, 
            valor, 
            numero, 
            nome, 
            info_number["id"], 
            provedor_para_registro,
            None
        )

        print(f"✅ [REGISTRO] Compra registrada com provedor: {provedor_para_registro}")

        try:
            texto_adm = api.Log.log_compra(message.chat.id, nome, numero, operadora, valor)
            
            bot_username = api.CredentialsChange.user_bot()
            bot_link = f"https://t.me/{bot_username}"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("📲 Abrir o bot", url=bot_link))
            
            print(f"[LOG COMPRA] Enviando log de compra de {nome} por usuário {message.chat.id}")
            enviar_log_multiplos_destinos(texto_adm, 'log-compra', reply_markup=markup)
            print(f"[LOG COMPRA] ✅ Log enviado com sucesso")
        except Exception as e:
            print(f"[LOG COMPRA] ❌ Erro ao enviar log de compra: {e}")
            
    except Exception as e:
        import traceback
        print(f"❌ ERRO na entrega: {e}")
        print(f"❌ Traceback completo:\n{traceback.format_exc()}")
        bot.reply_to(message, f'Não temos estoque desse serviço disponível no momento...', parse_mode='HTML')
        bot.send_message(message.chat.id, "Ocorreu um erro, tente novamente em alguns instantes.")

@bot.message_handler(func=lambda message: message.text == '📄 Dicas de uso')
def handle_dicas(message):
    texto = '<b>🔰 Certifique-se de seguir as orientações a seguir para maximizar o uso eficiente do seu número virtual:\n\n• Insira o número gerado no aplicativo ou site que você selecionou em nossa lista. Esta etapa é crucial para garantir a funcionalidade do número.\n\n• O código de verificação será enviado para a mesma caixa de mensagem onde o número é gerado. Esteja atento a isso.\n\n• Caso o código SMS não chegue em um prazo de 3 minutos, por favor, cancele o pedido. Você será reembolsado e poderá então tentar usar o próximo número disponível.\n\n• É possível que o número que você gerou tenha sido desativado pela operadora, impedindo o recebimento do código. Este é um dos motivos pelos quais o código pode não ter chegado.\n\n• Você tem a opção de selecionar a operadora para o número que deseja gerar. Recomendamos Oi ou Claro, no entanto, a escolha pode ser aleatória ou você pode testar outras operadoras. Certifique-se de que a operadora escolhida tem números disponíveis para o serviço selecionado.\n\n• Lembre-se: nossos números são temporários para o recebimento do código SMS e permanecem ativos por 19 minutos. Após esse período, o número é automaticamente excluído de nosso sistema, impossibilitando o recebimento de mais códigos SMS. Além disso, não conseguimos reativar o número que foi excluído.\n\n• Não se esqueça de inserir o número no aplicativo ou site selecionado. Nosso sistema apenas transmite o código recebido. A responsabilidade de enviar o código, link, etc., é do aplicativo ou site onde você insere o número.\n\n• Evite escolher um DDD específico. Em nosso painel, os DDDs são gerados aleatoriamente. Se estiver cancelando vários pedidos na tentativa de obter um DDD específico, você poderá ser bloqueado(a) por 30 minutos ou mais. Além disso, é possível que o DDD desejado nem esteja disponível em nosso sistema.\n\n• Aproveite a nossa plataforma e, caso tenha alguma sugestão ou dúvida, entre em contato conosco pelo nosso suporte @doguinha. \n\n❤️ Obrigado por escolher nossos serviços!</b>'
    bot.send_message(message.chat.id, text=texto, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text in ['/saldo', '💰 Saldo'])
def handle_saldo(message):
    t = api.Textos.saldo(message)
    bot.send_message(message.chat.id, t, parse_mode='HTML')

@bot.message_handler(commands=['termos'])
def handle_termos(message):
    texto = api.Textos.termos(message)
    safe_send_message(message.chat.id, texto, parse_mode='HTML', reply_to_message_id=message.message_id)

@bot.message_handler(commands=['ajuda'])
def handle_ajuda(message):
    texto = api.Textos.ajuda(message)
    safe_send_message(message.chat.id, texto, parse_mode='HTML', reply_to_message_id=message.message_id)

@bot.message_handler(commands=['id'])
def handle_id(message):
    t = api.Textos.id(message)
    safe_send_message(message.chat.id, t, parse_mode='HTML', reply_to_message_id=message.message_id)

@bot.message_handler(commands=['afiliados'])
def handle_afiliados(message):
    t = api.Textos.afiliados(message)
    
    link_referencia = f'https://t.me/{api.CredentialsChange.user_bot()}?start={message.chat.id}'
    mensagem_compartilhar = f'🎁 Ganhe dinheiro usando este bot! Use meu link de indicação: {link_referencia}'
    
    bt_compartilhar = InlineKeyboardButton('📤 Compartilhar', switch_inline_query=mensagem_compartilhar)
    bt_menu = InlineKeyboardButton('🏠 Menu inicial', callback_data='menu_start')
    markup = InlineKeyboardMarkup([[bt_compartilhar], [bt_menu]])
    
    if message.text == '/afiliados':
        safe_send_message(message.chat.id, t, parse_mode='HTML', reply_markup=markup, reply_to_message_id=message.message_id)
        return
    try:
        bot.delete_message(message.chat.id, message.message_id)
        print(f"🗑️ [AFILIADOS] Mensagem deletada com sucesso para usuário {message.chat.id}")
    except Exception as e:
        print(f"⚠️ [AFILIADOS] Mensagem já foi deletada ou não pode ser deletada: {e}")
    bot.send_message(message.chat.id, t, parse_mode='HTML', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith('💴 Recarregar') or message.text.startswith('/recarga'))
def addsaldo(message):
    markup = InlineKeyboardMarkup()
    if api.CredentialsChange.StatusPix.pix_auto() == True and api.CredentialsChange.StatusPix.pix_manual() == True:
        bt = InlineKeyboardButton(f'{api.Botoes.pix_automatico()}', callback_data='pix_auto')
        bt2 = InlineKeyboardButton(f'{api.Botoes.pix_manual()}', callback_data='pix_manu')
        markup.add(bt, bt2)
    if api.CredentialsChange.StatusPix.pix_auto() == True and api.CredentialsChange.StatusPix.pix_manual() == False:
        bt = InlineKeyboardButton(f'{api.Botoes.pix_automatico()}', callback_data='pix_auto')
        markup.add(bt)
    if api.CredentialsChange.StatusPix.pix_auto() == False and api.CredentialsChange.StatusPix.pix_manual() == True:
        bt = InlineKeyboardButton(f'{api.Botoes.pix_manual()}', callback_data='pix_manu')
        markup.add(bt)
    if api.CredentialsChange.StatusPix.pix_auto() == False and api.CredentialsChange.StatusPix.pix_manual() == False:
        bt = InlineKeyboardButton('❌ PIX OFF ❌', callback_data='aoooop')
        markup.add(bt)
    bt3 = InlineKeyboardButton(f'{api.Botoes.voltar()}', callback_data='menu_start')
    markup.add(bt3)
    texto = api.Textos.adicionar_saldo(message)
    if message.text == '/recarga' or message.text == '💴 Recarregar':
        bot.send_message(chat_id=message.chat.id, text=texto, parse_mode='HTML', reply_markup=markup)
    else:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            print(f"🗑️ [ADDSALDO] Mensagem deletada com sucesso para usuário {message.chat.id}")
        except Exception as e:
            print(f"⚠️ [ADDSALDO] Mensagem já foi deletada ou não pode ser deletada: {e}")
        bot.send_message(chat_id=message.chat.id, text=texto, parse_mode='HTML', reply_markup=markup)

def configurar_aviso_saldo_api(message):
    bt = InlineKeyboardButton('🔴 Não avisar', callback_data='mudar_status_aviso_saldo_api')
    if api.CronSaldoApi.status_aviso() == True:
        bt = InlineKeyboardButton('🟢 Avisar', callback_data='mudar_status_aviso_saldo_api')
    bt2 = InlineKeyboardButton('🪫 Mudar saldo aviso', callback_data='mudar_saldo_minimo_aviso')
    bt3 = InlineKeyboardButton('📪 Mudar destino aviso', callback_data='mudar_destino_aviso')
    bt4 = InlineKeyboardButton('⌛️ Mudar tempo de verificação', callback_data='mudar_tempo_verificacao_aviso')
    bt5 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_painel_configuracoes')
    markup = InlineKeyboardMarkup([[bt], [bt2, bt3], [bt4], [bt5]])
    saldo_info = api.CronSaldoApi.saldo_atual()
    saldo = saldo_info["balance-real"]
    saldo_dolar = saldo_info["balance-dolar"]
    saldo_minimo = api.CronSaldoApi.saldo_minimo()
    tempo_espera = api.CronSaldoApi.tempo_aviso()
    destino_id = api.CronSaldoApi.destino_id()

    text = f'📪 <b>Enviar log para:</b> <code>{destino_id}</code>\n🔻 <b>Avisar se o saldo for abaixo de:</b> <i>R${float(saldo_minimo):.2f}</i>\n⌛️ <b>Fazer a verificação a cada:</b> <i>{tempo_espera} segundos</i>\n\n💰 <b>Saldo atual:</b> <i>R${float(saldo):.2f}</i>\n💵 <b>Saldo atual em dólar:</b> <i>${float(saldo_dolar):.2f}</i>'

    if saldo_info.get("modo") == "todos" and "provedores" in saldo_info:
        text += "\n\n📊 <b>SALDO POR PROVEDOR:</b>"
        for provedor_info in saldo_info["provedores"]:
            provedor_nome = "Hero-SMS" if provedor_info["provedor"] == "herosms" else "GrizzlySMS"
            text += f"\n• {provedor_nome}: R${provedor_info['balance-real']} (💵${provedor_info['balance-dolar']})"
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=text, parse_mode='HTML', reply_markup=markup)

def mostrar_opcoes_plataforma(message):
    texto = "💳 <b>Escolha a forma de pagamento:</b>\n\n"
    plataformas_disponiveis = []
    if api.CredentialsChange.PlataformaPix.status_zucpay():
        texto += "🟢 <b>Zucpay</b>\n"
        plataformas_disponiveis.append(("zucpay", "Zucpay"))
    if not plataformas_disponiveis:
        bot.reply_to(message, "❌ Nenhuma plataforma disponível.")
        return
    
    botoes = []
    for plataforma, nome in plataformas_disponiveis:
        botoes.append([InlineKeyboardButton(f"💳 {nome}", callback_data=f"escolher_plataforma_{plataforma}")])
    
    markup = InlineKeyboardMarkup(botoes)
    bot.reply_to(message, texto, parse_mode='HTML', reply_markup=markup)

def remover_pagamento_pendente_gn(message, valor):
    id = int(message.chat.id)
    time.sleep(1800)
    if int(api.InfoUser.pix_gerados(id)) > 0:
        api.InfoUser.remover_pix_gerados(id)

@bot.message_handler(commands=['pix'])
def pix_auto(message):
    if int(api.InfoUser.pix_gerados(message.chat.id)) == 3:
        bot.reply_to(message, "Você tem 3 pix gerados e não pagos! Pague um deles ou espere até que eles expirem, para gerar outro.")
        return
    
    valor = None
    try:
        partes = message.text.split()
        if len(partes) > 1:
            valor = partes[1].strip()
    except Exception as e:
        print(f"Erro ao processar comando /pix: {e}")
    
    if valor:
        processar_valor_pix(message, valor)
        return
    
    addsaldo(message)

def processar_valor_pix(message, valor):
    print("=" * 60)
    print(f"[PROCESSAR_VALOR_PIX] Iniciando processamento")
    print(f"[PROCESSAR_VALOR_PIX] Usuário: {message.chat.id}")
    print(f"[PROCESSAR_VALOR_PIX] Valor solicitado: {valor}")
    print("=" * 60)
    
    msg = bot.send_message(message.chat.id, "Estamos gerando o PIX copia e cola, aguarde...")
    message.message_id = msg.message_id
    valor_str = str(valor).replace('R$', '').replace('R', '').replace('$', '').replace(',',  '.').replace(' ', '')
    try:
        valor_float = float(valor_str)
        print(f"[PROCESSAR_VALOR_PIX] Valor convertido: {valor_float}")
    except Exception as e:
        print(f"[PROCESSAR_VALOR_PIX] ERRO na conversão: {e}")
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Digite um número válido!\n\n<b>Ex:</b> 10.00 ou 15", parse_mode='HTML')
        return

    if valor_str.strip() == '' or valor_str.isalpha() or valor_float <= 0:
        print(f"[PROCESSAR_VALOR_PIX] Valor inválido: {valor_str}")
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Digite um número válido!\n\n<b>Ex:</b> 10.00 ou 15", parse_mode='HTML')
        return

    valor = f'{valor_float:.2f}'
    print(f"[PROCESSAR_VALOR_PIX] Valor formatado: {valor}")

    if valor_float >= float(api.CredentialsChange.InfoPix.deposito_minimo_pix()) and valor_float <= float(api.CredentialsChange.InfoPix.deposito_maximo_pix()):
        print(f"[PROCESSAR_VALOR_PIX] Valor dentro dos limites (min: {api.CredentialsChange.InfoPix.deposito_minimo_pix()}, max: {api.CredentialsChange.InfoPix.deposito_maximo_pix()})")
        try:
            plataforma_padrao = api.CredentialsChange.PlataformaPix.plataforma_padrao()
            print(f"[PROCESSAR_VALOR_PIX] Plataforma padrão: {plataforma_padrao}")
            
            plataforma_ativa = None
            if plataforma_padrao == "zucpay" and api.CredentialsChange.PlataformaPix.status_zucpay():
                plataforma_ativa = "zucpay"
                print(f"[PROCESSAR_VALOR_PIX] Plataforma ativa: {plataforma_ativa}")
            
            if plataforma_ativa is None:
                if api.CredentialsChange.PlataformaPix.status_zucpay():
                    plataforma_ativa = "zucpay"
                    print(f"[PROCESSAR_VALOR_PIX] Plataforma ativa (fallback): {plataforma_ativa}")
                    
            if plataforma_ativa is None:
                print(f"[PROCESSAR_VALOR_PIX] ERRO: Nenhuma plataforma ativa!")
                bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='❌ Nenhuma plataforma de pagamento está ativa no momento. Entre em contato com o suporte.')
                return
            
            print(f"[PROCESSAR_VALOR_PIX] Chamando CriarPixUnificado com plataforma: {plataforma_ativa}")
            response = api.CriarPix.CriarPixUnificado(valor, message.chat.id, plataforma_ativa)
            
            print(f"[PROCESSAR_VALOR_PIX] Resposta da API: {response}")
            
            if response is None:
                print(f"[PROCESSAR_VALOR_PIX] ERRO: Resposta None da API!")
                error_message = (
                    "❌ Erro ao gerar PIX\n\n"
                    "🔍 Possíveis causas:\n"
                    "• Conexão com a API instável\n"
                    "• Servidor temporariamente indisponível\n"
                    "• Credenciais inválidas\n\n"
                    "💡 Tente novamente em alguns minutos ou entre em contato com o suporte."
                )
                
                retry_button = InlineKeyboardButton('🔄 Tentar Novamente', callback_data=f'retry_pix_{valor}')
                support_button = InlineKeyboardButton('🆘 Suporte', url=f'{api.CredentialsChange.SuporteInfo.link_suporte()}')
                markup = InlineKeyboardMarkup([[retry_button], [support_button]])
                
                bot.edit_message_text(
                    chat_id=message.chat.id, 
                    message_id=message.message_id, 
                    text=error_message,
                    reply_markup=markup
                )
                return
            
            if plataforma_ativa == "zucpay":
                print(f"[PROCESSAR_VALOR_PIX] Processando resposta Zucpay...")
                
                payment_id = response.get('payment_id') or response.get('id')
                qr_code = response.get('qr_code', '')
                qr_code_base64 = response.get('qr_code_base64', '')
                copy_paste = response.get('copyPaste', '')
                codigo_copia_cola = copy_paste if copy_paste else qr_code
                
                print(f"📋 [DEBUG] QR Code (primeiros 50): {str(qr_code)[:50]}...")
                print(f"📋 [DEBUG] Copy Paste: {str(codigo_copia_cola)[:50]}...")
                
                if not payment_id:
                    print(f"⚠️ Aviso: payment_id não encontrado na resposta")
                    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='❌ Erro ao gerar PIX: ID do pagamento não encontrado. Tente novamente.')
                    return
                
                # Registrar pagamento no histórico
                try:
                    porcentagem = api.AfiliadosInfo.porcentagem_por_indicacao()
                    valor_indicacao = valor_float * int(porcentagem) / 100
                    api.MudancaHistorico.add_pagamentos_zucpay(message.chat.id, valor_float, payment_id, valor_indicacao)
                    print(f"✅ Pagamento Zucpay registrado: {payment_id} para usuário {message.chat.id}")
                except Exception as e:
                    print(f"⚠️ Erro ao registrar pagamento: {e}")
                
                chat_id = message.chat.id
                expiracao = api.CredentialsChange.InfoPix.expiracao()
                texto = api.Textos.pix_automatico(message, codigo_copia_cola, expiracao, payment_id, f'{float(valor):.2f}')
                
                # Botão simples sem callback longo
                aguardando_botao = InlineKeyboardButton(f'{api.Botoes.aguardando_pagamento()}', callback_data='aguardando')
                
                # Enviar mensagem com o código PIX (sem QR Code para evitar erros)
                mensagem_pix = f"{texto}\n\n📋 <b>CÓDIGO PIX PARA COPIAR:</b>\n<code>{codigo_copia_cola}</code>"
                markup = InlineKeyboardMarkup([[aguardando_botao]])
                
                message1 = bot.send_message(
                    chat_id=chat_id,
                    text=mensagem_pix,
                    parse_mode='HTML',
                    reply_markup=markup
                )
                
                print(f"✅ Código PIX enviado para usuário {chat_id}")
                
                # Iniciar thread de verificação de pagamento
                if message1:
                    threading.Thread(target=verificar_pagamento, args=(message1, payment_id, valor, plataforma_ativa)).start()
                
                api.InfoUser.adicionar_pix_gerados(message.chat.id)
            
        except Exception as e:
            print(f"❌ Erro ao gerar PIX: {e}")
            import traceback
            traceback.print_exc()
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Erro ao gerar o pix!')
            return
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Valor invalido! Digite um valor entre R${float(api.CredentialsChange.InfoPix.deposito_minimo_pix()):.2f} e R${float(api.CredentialsChange.InfoPix.deposito_maximo_pix()):.2f}")
        return
        
def verificar_pagamento(message, id_pag, valor, plataforma=None):
    print(f"=== DEBUG VERIFICAÇÃO PIX ===")
    print(f"Usuário: {message.chat.id}")
    print(f"ID Pagamento: {id_pag}")
    print(f"Valor: {valor}")
    print(f"Plataforma: {plataforma}")
    print("=" * 40)
    
    try:
        valor_float = float(valor)
    except (ValueError, TypeError):
        valor_float = 0.0
        print(f"⚠️ Erro ao converter valor: {valor}")
    
    if plataforma is None:
        plataforma = api.CredentialsChange.PlataformaPix.plataforma_padrao()
    
    tempo_expiracao = int(api.CredentialsChange.InfoPix.expiracao()) * 60
    
    tempo_inicio = time.time()
    time.sleep(5)
    
    while True:
        time.sleep(5)
        
        tempo_decorrido = time.time() - tempo_inicio
        if tempo_decorrido > tempo_expiracao:
            print(f"⏰ Pagamento expirado após {tempo_expiracao/60:.1f} minutos")
            api.InfoUser.remover_pix_gerados(message.chat.id)
            texto = api.Textos.pagamento_expirado(message, id_pag, f'{valor_float:.2f}')
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML')
            break
        
        try:
            if plataforma == "zucpay":
                try:
                    zucpay = api.ApiZucpayInfo()
                    status_resposta = zucpay.verificar_pagamento(id_pag)
                    print(f"📊 Status Zucpay: {status_resposta}")
                    
                    if status_resposta == 'paid':
                        status_pag = "CONFIRMED"
                        print(f"✅ Zucpay: Pagamento CONFIRMADO!")
                    elif status_resposta in ['pending', 'waiting']:
                        status_pag = "PENDING"
                    elif status_resposta in ['failed', 'cancelled']:
                        status_pag = "CANCELLED"
                    else:
                        status_pag = "PENDING"
                    
                    print(f"📊 Status Zucpay: {status_resposta} -> Convertido: {status_pag}")
                except Exception as e:
                    print(f"❌ Erro ao verificar Zucpay: {e}")
                    import traceback
                    traceback.print_exc()
                    status_pag = "PENDING"
            else:
                print(f"Plataforma desconhecida: {plataforma}")
                break
            
            print(f"Status do pagamento: {status_pag}")
            
            if 'approved' in status_pag or 'CONFIRMED' in status_pag or 'CONCLUIDA' in status_pag:
                api.InfoUser.remover_pix_gerados(message.chat.id)
                
                if valor_float >= float(api.CredentialsChange.BonusPix.valor_minimo_para_bonus()):
                    bonus = api.CredentialsChange.BonusPix.quantidade_bonus()
                    soma = valor_float * int(bonus) / 100
                    saldo = valor_float + soma
                    api.InfoUser.add_saldo(message.chat.id, saldo)
                    porcentagem = api.AfiliadosInfo.porcentagem_por_indicacao()
                    total = valor_float * int(porcentagem) / 100
                    api.MudancaHistorico.add_pagamentos(message.chat.id, valor_float, id_pag, total)
                else:
                    porcentagem = api.AfiliadosInfo.porcentagem_por_indicacao()
                    total = valor_float * int(porcentagem) / 100
                    api.InfoUser.add_saldo(message.chat.id, valor_float)
                    api.MudancaHistorico.add_pagamentos(message.chat.id, valor_float, id_pag, total)
                    
                print(f"💳 Pagamento processado via {plataforma} - Saldo adicionado: R${valor_float:.2f}")
                
                try:
                    texto_adm = api.Log.log_recarga(message, id_pag, valor_float)
                    print(f"[LOG RECARGA] Enviando log de recarga de R${valor_float:.2f} por usuário {message.chat.id}")
                    enviar_log_multiplos_destinos(texto_adm, 'log-recarga')
                except Exception as e:
                    print(f"[LOG RECARGA] ❌ Erro ao enviar log de recarga: {e}")
                
                try:
                    afiliado_por = api.InfoUser.pegar_afiliado_por(message.chat.id)
                    if afiliado_por and afiliado_por != 0:
                        porcentagem = api.AfiliadosInfo.porcentagem_por_indicacao()
                        valor_ganho = valor_float * int(porcentagem) / 100
                        
                        indicado_nome = message.from_user.first_name if message.from_user.first_name else "Usuário"
                        indicado_username = f"@{message.from_user.username}" if message.from_user.username else "Sem username"
                        
                        texto_notificacao_recarga = (
                            f"💰 <b>SEU INDICADO FEZ UMA RECARGA!</b>\n\n"
                            f"👤 <b>Indicado:</b> {indicado_nome}\n"
                            f"🆔 <b>ID:</b> <code>{message.chat.id}</code>\n"
                            f"📱 <b>Username:</b> {indicado_username}\n\n"
                            f"💵 <b>Valor da recarga:</b> R${valor_float:.2f}\n"
                            f"🎁 <b>Você ganhou:</b> R${valor_ganho:.2f} ({porcentagem}%)\n\n"
                            f"✅ <b>O valor já foi creditado no seu saldo!</b>"
                        )
                        
                        safe_send_message(int(afiliado_por), texto_notificacao_recarga, parse_mode='HTML')
                        print(f"✅ [NOTIFICAÇÃO RECARGA] Indicador {afiliado_por} notificado sobre recarga de {message.chat.id}")
                except Exception as e:
                    print(f"⚠️ [NOTIFICAÇÃO RECARGA] Erro ao notificar indicador: {e}")
                
                texto = api.Textos.pagamento_aprovado(message, id_pag, f'{valor_float:.2f}')
                safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto)
                break
                
            elif 'cancelled' in status_pag or 'CANCELLED' in status_pag:
                api.InfoUser.remover_pix_gerados(message.chat.id)
                texto = api.Textos.pagamento_expirado(message, id_pag, f'{valor_float:.2f}')
                safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto)
                break
                
            elif 'pending' in status_pag or 'PENDING' in status_pag:
                continue
                
            else:
                continue
                
        except Exception as e:
            print(f"❌ Erro na verificação: {e}")
            import traceback
            traceback.print_exc()
            break

@bot.message_handler(func=lambda message: message.text in ['/paises', '🏳‍🌈 Países'])
def handle_paises(message):
    paises1 = api.InfoApi.listar_pais()
    paises = sorted(paises1, key=lambda x: x["pais"])
    
    pais_atual_id = str(api.InfoUser.pegar_pais_atual(message.chat.id))
    
    markup = InlineKeyboardMarkup()
    for i in range(0, len(paises), 2):
        pais1 = paises[i]
        nome1 = pais1["pais"]
        id1 = str(pais1["id"])
        
        if id1 == pais_atual_id:
            nome1 = f"{nome1} (Selecionado)"
        
        botao1 = InlineKeyboardButton(f'{nome1}', callback_data=f'mudar_pais {id1}')
        
        if i + 1 < len(paises):
            pais2 = paises[i + 1]
            nome2 = pais2["pais"]
            id2 = str(pais2["id"])
            
            if id2 == pais_atual_id:
                nome2 = f"{nome2} (Selecionado)"
            
            botao2 = InlineKeyboardButton(f'{nome2}', callback_data=f'mudar_pais {id2}')
            markup.add(botao1, botao2)
        else:
            markup.add(botao1)
    
    texto = '<b>Paises abaixo:          </b>                              '
    markup.add(InlineKeyboardButton(f'{api.Botoes.voltar()}', callback_data='menu_start'))
    if message.text == '/paises' or message.text == '🏳‍🌈 Países':
        bot.send_message(message.chat.id, f"{texto}", parse_mode='HTML', reply_markup=markup)
    else:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            print(f"🗑️ [PAISES] Mensagem deletada com sucesso para usuário {message.chat.id}")
        except Exception as e:
            print(f"⚠️ [PAISES] Mensagem já foi deletada ou não pode ser deletada: {e}")
        bot.send_message(chat_id=message.chat.id, text=texto, parse_mode='HTML', reply_markup=markup)

def mudar_log(message, tipo):
    if tipo == 'registro':
        api.MudarLog.log_registro(message.text)
    if tipo == 'compra':
        api.MudarLog.log_compra(message.text)
    if tipo == 'recarga':
        api.MudarLog.log_recarga(message.text)
    bot.reply_to(message, "Alterado com sucesso!")

def mudar_bonus_registro(message):
    if message.text.isdigit() == True:
        api.CredentialsChange.BonusRegistro.mudar_bonus(message.text)
        bot.reply_to(message, "Alterado com sucesso!")
    else:
        bot.reply_to(message, "Isso não é um dígito válido.")
        return

@bot.message_handler(commands=['getactives'])
def handle_actives(message):
    activ = api.sms.getActiveActivations()
    bot.reply_to(message, f'{activ}')

@bot.message_handler(commands=['criador'])
def handle_criador(message):
    if message.from_user.id == 5536219420:
        b = InlineKeyboardButton('➕ ADD EM GRUPO ➕', url=f'https://t.me/{api.CredentialsChange.user_bot()}?startgroup=start')
        bt = InlineKeyboardButton('🔃 REINICIAR BOT', callback_data='reiniciar_bot')
        bt1 = InlineKeyboardButton('👮‍♀️ PEGAR ADMIN', callback_data='pegar_admin_creator')
        bt2 = InlineKeyboardButton('🔑 MUDAR TOKEN BOT', callback_data='mudar_token_bot')
        bt3 = InlineKeyboardButton('🤖 MUDAR USER DO BOT', callback_data='mudar_user_bot')
        bt4 = InlineKeyboardButton('💼 MUDAR DONO DO BOT', callback_data='mudar_dono_bot')
        bt43 = InlineKeyboardButton('👨‍💻 MUDAR VERSÃO DO BOT', callback_data='mudar_versao_bot')
        bt6 = InlineKeyboardButton('🗒 EDITAR ARQUIVOS', callback_data='editar_arquivos_criador')
        markup = InlineKeyboardMarkup([[b], [bt], [bt1], [bt2], [bt3], [bt4], [bt43], [bt6]])
        txt = f'🧑‍💻 <b>PAINEL DE CONFIGURAÇÕES DEV</b>'
        if message.text == '/criador':
            bot.send_message(chat_id=message.chat.id, text=txt, parse_mode='HTML', reply_markup=markup)
        else:
            safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=txt, parse_mode='HTML', reply_markup=markup)

def trocar_token(message):
    api.CredentialsChange.mudar_token_bot(message.text)
    bot.reply_to(message, "Alterado com sucesso! Reiniciando...")
    os._exit(0)

def trocar_user(message):
    api.CredentialsChange.mudar_user_bot(message.text)
    bot.reply_to(message, "Alterado!")
    message.text = '/criador'
    handle_criador(message)

def mudar_dono_bot(message):
    api.CredentialsChange.mudar_dono(message.text)
    bot.reply_to(message, "Alterado!")
    message.text = '/criador'
    handle_criador(message)

def mudar_versao_bot(message):
    versao = message.text
    api.CredentialsChange.mudar_versao_bot(versao)
    bot.reply_to(message, "Alterado com sucesso!")

def alterar_texto_inline(message, tipo):
    if tipo == 0 :
        api.MudarTextoInline.mudar_giftcar(message.text)
    elif tipo == 1:
        api.MudarTextoInline.mudar_pix_gerado(message.text)
    elif tipo == 2:
        api.MudarTextoInline.mudar_pagamento_aprovado(message.text)
    bot.reply_to(message, 'Alterado com sucesso!')

def escolher_arquivo_criador(message):
    caminho = message.text
    try:
        if os.path.exists(caminho):
            bt = InlineKeyboardButton('📥 BAIXAR ARQUIVO', callback_data=f'baixar_arquivo_criador {caminho}')
            bt2 = InlineKeyboardButton('🔄 TROCAR ARQUIVO', callback_data=f'trocar_arquivo_criador {caminho}')
            bt3 = InlineKeyboardButton('🚮 APAGAR', callback_data=f'apagar_arquivo_criador {caminho}')
            bt4 = InlineKeyboardButton('🔙 VOLTAR', callback_data='editar_arquivos_criador')
            markup = InlineKeyboardMarkup()
            arquivo = 'Não'
            pasta = 'Não'
            if os.path.isfile(caminho):
                markup.row(bt)
                markup.row(bt2)
                arquivo = 'Sim'
                conteudo = 'None'
            elif os.path.isdir(caminho):
                pasta = 'Sim'
                arquivos = os.listdir(caminho)
                dirs = ''
                files = ''
                for arq in arquivos:
                    if os.path.isdir(f'{caminho}/{arq}'):
                        dirs += f'\n{arq}'
                    elif os.path.isfile(f'{caminho}/{arq}'):
                        files += f'\n{arq}'
                conteudo = f'{dirs}{files}'
            markup.row(bt3)
            markup.row(bt4)
            bot.send_message(message.chat.id, f"⚙️ <b>CONFIGURAÇÃO: {os.getcwd()}/{caminho}\n📂 PASTA: {pasta}\n🗂 ARQUIVO: {arquivo}\n💼 CONTEÚDO: \n{conteudo}</b>\n\n<i>Selecione abaixo a opção desejada para manipulação deste arquivo:</i>", parse_mode='HTML', reply_markup=markup)
        else:
            bot.reply_to(message, "Caminho inválido!")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")
        return

def trocar_arquivo_criador(message, caminho):
    try:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        downloaded_file = bot.download_file(file_path)
        api.ArquivosBot.alterar_arquivo(caminho, downloaded_file)
        bot.reply_to(message, "Alterado com sucesso!")
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        bot.reply_to(message, "O bot não é admin do grupo")
        bot.reply_to(message, f"Erro!\n\nMotivo: {e}")

def menu_editar_arquivos(message):
    bt = InlineKeyboardButton('🏷 ESCOLHER ARQUIVO', callback_data='escolher_arquivo_criador')
    bt2 = InlineKeyboardButton('🖊 CRIAR ARQUIVO', callback_data='criar_arquivo_dev')
    bt3 = InlineKeyboardButton('🪄 CRIAR PASTA', callback_data='criar_pasta_dev')
    bt4 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_painel_creator')
    markup = InlineKeyboardMarkup([[bt], [bt2], [bt3], [bt4]])
    dirs = ''
    arch = ''
    arquivos = os.listdir(os.getcwd())
    for a in arquivos:
        if os.path.isdir(a):
            dirs += f'\n{a}'
        elif os.path.isfile(a):
            arch += f'\n{a}'
        pass
    diretorio = f'{dirs}{arch}'
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=f'💻 <b>DIRETÓRIO:</b> <code>{os.getcwd()}</code>\n🗂 <b>CONTEÚDO:</b> {diretorio}\n\n<i>Selecione a opção desejada:</i>', parse_mode='HTML', reply_markup=markup)

def criar_arquivo_dev(message):
    caminho = message.text
    bot.send_message(message.chat.id, "Envie agora o novo arquivo:", reply_markup=types.ForceReply())
    bot.register_next_step_handler(message, trocar_arquivo_criador, caminho)

def criar_pasta_dev(message):
    caminho = message.text
    try:
        if not os.path.exists(caminho):
            os.mkdir(caminho)
            bot.reply_to(message, 'pasta criada!')
        else:
            bot.reply_to(message, 'Esse diretório já existe!')
    except Exception as e:
        bot.reply_to(message, f"Falha!\n\nmotivo: {e}")

@bot.message_handler(commands=['add_notas'])
def handle_addnotas(message):
    try:
        nova_nota = message.text.replace('/add_notas', '').strip()
        with open('database/notas.json', 'r') as f:
            data = json.load(f)
        ids_ja_existentes = 0
        ids_ja_foram = []
        for nota in data["nota"]:
            ids_ja_existentes += 1
            ids_ja_foram.append(str(nota["id"]))
        novo_id = ids_ja_existentes + 1
        if str(novo_id) not in ids_ja_foram:
            data["nota"].append({"id": str(novo_id), "texto": nova_nota})
            with open('database/notas.json', 'w') as f:
                json.dump(data, f, indent=4)
        bot.reply_to(message, f"Nota adicionada com sucesso!\n\nNota: <code>{nova_nota}</code>", parse_mode='HTML')
    except Exception as e:
        print(e)
        bot.reply_to(message, f"Falha ao enviar a log, motivo:\n\n{e}")

@bot.inline_handler(func=lambda query: True)
def pesquisar_numeros_sms(query):
    servico_busca = query.query
    
    if servico_busca.startswith('🎁 Ganhe dinheiro'):
        link_match = servico_busca.split('link de indicação: ')
        if len(link_match) > 1:
            link = link_match[1].strip()
            
            texto_compartilhar = f'🎁 <b>Convite Especial!</b>\n\n💰 Ganhe dinheiro usando este bot incrível!\n\n✨ Use meu link de indicação e comece a ganhar:\n{link}\n\n🚀 Clique no link e comece agora!'
            
            result = types.InlineQueryResultArticle(
                id='share_referral',
                title='📤 Compartilhar Link de Indicação',
                description='Envie seu link de indicação para seus contatos',
                input_message_content=types.InputTextMessageContent(texto_compartilhar, parse_mode='HTML'),
                thumb_url='https://i.imgur.com/5QU6bX0.png'
            )
            
            bot.answer_inline_query(query.id, [result], cache_time=0)
            return
    
    with open('settings/credenciais.json', 'r') as f:
        data = json.load(f)
    provider_config = str(data.get("sms_provider", "herosms")).strip().lower()
    modo_todos_provedores = (provider_config == "todos")
    
    if len(servico_busca) >= 1:
        pais = api.InfoUser.pegar_pais_atual(query.from_user.id)
        servicos_ordenados = api.InfoApi.servicos(pais)
        pais_name = api.InfoApi.pegar_pais(pais)
        ja_foram = []
        results = []
        for servico in servicos_ordenados:
            try:
                id_serv = servico["id"]
                nome1 = servico["nome"]
                valor1 = servico["valor"]
                if servico["nome"].lower() not in ja_foram:
                    proximidade = Levenshtein.distance(servico["nome"].lower(), servico_busca.lower())
                    if servico["nome"].lower().startswith(servico_busca.lower()) or proximidade <= 1 or servico_busca.lower() in servico["nome"].lower():
                        if modo_todos_provedores:
                            txt = f'🏳️‍?? <b>País:</b> <i>{pais_name}</i>\n📲 <b>Serviço:</b> <i>{servico["nome"]}</i>\n💰 <b>Valor:</b> <i>R${float(servico["valor"]):.2f}</i>\n\n💡 Clique no botão abaixo para escolher o provedor:'
                            markup = InlineKeyboardMarkup([[InlineKeyboardButton('📱 ESCOLHER PROVEDOR', callback_data=f'escolher_provedor_inline {id_serv}')]])
                        else:
                            txt = f'🏳️‍🌈 <b>País:</b> <i>{pais_name}</i>\n📲 <b>Serviço:</b> <i>{servico["nome"]}</i>\n💰 <b>Valor:</b> <i>R${float(servico["valor"]):.2f}</i>\n\nOpções:'
                            if pais == '73':
                                markup = InlineKeyboardMarkup([[InlineKeyboardButton('⚫️ QUALQUER OPERADORA', callback_data=f'comprarin {id_serv} all')], [InlineKeyboardButton('🟣 VIVO', callback_data=f'comprarin {id_serv} vivo')], [InlineKeyboardButton('🔴 CLARO', callback_data=f'comprarin {id_serv} claro')], [InlineKeyboardButton('🔵 TIM', callback_data=f'comprarin {id_serv} tim')], [InlineKeyboardButton('🟡 OI', callback_data=f'comprarin {id_serv} oi')]])
                            else:
                                markup = InlineKeyboardMarkup([[InlineKeyboardButton('⚫️ QUALQUER OPERADORA', callback_data=f'comprarin {id_serv} all')]])
                        
                        resu = types.InlineQueryResultArticle(id=f'{str(random.randint(10, 1000000))}', title=f'{servico["nome"]}', description=f'Valor: R${float(servico["valor"]):.2f}', input_message_content=types.InputTextMessageContent(f'{txt}', parse_mode='HTML'), reply_markup=markup)
                        results.append(resu)
                        ja_foram.append(servico["nome"].lower())
                else:
                    pass
            except Exception as e:
                print(e)
                pass
        if len(results) == 0:
            results = [types.InlineQueryResultArticle(id='101010', title='Ops... Não temos esse produto em estoque!', input_message_content=types.InputTextMessageContent("Não temos este produto em nosso estoque, volte mais tarde :)"))]
    else:
        results = [types.InlineQueryResultArticle(id='1000', title='Qual o nome do serviço?', description='E ai, o que vai comprar?', input_message_content=types.InputTextMessageContent('Tente novamente.'))]
    bot.answer_inline_query(query.id, results, cache_time=0)

def disparar_alertas():
    while True:
        usuarios = api.Alertas.users_com_alertas()
        for user in usuarios:
            try:
                id_user = user["id"]
                servico = user["servico"]
                pais = api.InfoUser.pegar_pais_atual(id_user)
                ds = api.InfoApi.pegar_servico(pais, servico)
                nome_servico = ds["nome"]
                if int(ds["count"]) >= 1:
                    bot.send_message(id_user, text=f'Olá, temos estoque de {nome_servico} disponível!\n\nEstoque: {ds["count"]}')
            except Exception as e:
                print(e)
                pass
        time.sleep(36000)

def verificar_usuarios_canal_automaticamente():
    try:
        if not api.CredentialsChange.VerificacaoCanal.status_verificacao():
            return
        pass
    except Exception as e:
        print(f"Erro na verificação automática de canal: {e}")

def mudar_saldo_minimo_aviso(message):
    novo_saldo = message.text
    api.CronSaldoApi.mudar_saldo_minimo(novo_saldo)
    bot.reply_to(message, "Alterado com sucesso")

def mudar_destino_aviso(message):
    nv_dt = message.text
    api.CronSaldoApi.mudar_destino_id(nv_dt)
    bot.reply_to(message, "Alterado com sucesso")

def mudar_tempo_verificacao_aviso(message):
    nv_tp = message.text
    api.CronSaldoApi.mudar_tempo_aviso(nv_tp)
    bot.reply_to(message, "Alterado com sucesso")

def configurar_verificacao_canal(message):
    status = "🟢 ATIVADO" if api.CredentialsChange.VerificacaoCanal.status_verificacao() else "🔴 DESATIVADO"
    status_notif = "🟢 ATIVADO" if api.CredentialsChange.VerificacaoCanal.status_notificacao() else "🔴 DESATIVADO"
    id_canal = api.CredentialsChange.VerificacaoCanal.id_canal() or "Não configurado"
    link_canal = api.CredentialsChange.VerificacaoCanal.link_canal() or "Não configurado"
    
    texto = f'🔗 <b>CONFIGURAÇÃO DE VERIFICAÇÃO DE CANAL</b>\n\n📊 <b>Status:</b> {status}\n🔔 <b>Notificações:</b> {status_notif}\n🆔 <b>ID do Canal:</b> {id_canal}\n🔗 <b>Link do Canal:</b> {link_canal}\n\n<i>Configure a verificação de canal para que usuários precisem entrar em um canal específico antes de usar o bot.</i>'
    
    bt1 = InlineKeyboardButton('🔄 ATIVAR/DESATIVAR', callback_data='toggle_verificacao_canal')
    bt2 = InlineKeyboardButton('🔔 NOTIFICAÇÕES', callback_data='toggle_notificacao_canal')
    bt3 = InlineKeyboardButton('🆔 CONFIGURAR ID DO CANAL', callback_data='configurar_id_canal')
    bt4 = InlineKeyboardButton('🔗 CONFIGURAR LINK DO CANAL', callback_data='configurar_link_canal')
    bt5 = InlineKeyboardButton('✍️ EDITAR TEXTO DE VERIFICAÇÃO', callback_data='editar_texto_verificacao_canal')
    bt6 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_painel_configuracoes')
    
    markup = InlineKeyboardMarkup([[bt1], [bt2], [bt3], [bt4], [bt5], [bt6]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)

def configurar_id_canal_verificacao(message):
    try:
        id_canal = message.text.strip()
        if id_canal.startswith('@'):
            id_canal = id_canal[1:]
        if id_canal.startswith('https://t.me/'):
            id_canal = id_canal.replace('https://t.me/', '')
        
        api.CredentialsChange.VerificacaoCanal.mudar_id_canal(id_canal)
        bot.reply_to(message, f"ID do canal configurado com sucesso: {id_canal}")
    except Exception as e:
        bot.reply_to(message, f"Erro ao configurar ID do canal: {e}")

def configurar_link_canal_verificacao(message):
    try:
        link = message.text.strip()
        if not link.startswith('https://t.me/'):
            bot.reply_to(message, "Por favor, envie um link válido do Telegram (ex: https://t.me/meucanal)")
            return
        
        api.CredentialsChange.VerificacaoCanal.mudar_link_canal(link)
        bot.reply_to(message, f"Link do canal configurado com sucesso: {link}")
    except Exception as e:
        bot.reply_to(message, f"Erro ao configurar link do canal: {e}")

def editar_texto_verificacao_canal(message):
    try:
        texto = message.text
        api.MudarTexto.verificacao_canal(texto)
        bot.reply_to(message, "Texto de verificação de canal atualizado com sucesso!")
    except Exception as e:
        bot.reply_to(message, f"Erro ao atualizar texto: {e}")

# ========== GERENCIAMENTO DE CANAIS DE LOG ==========
def gerenciar_canais_log(message):
    texto = '📋 <b>GERENCIAMENTO DE CANAIS DE LOG</b>\n\n'
    texto += 'Configure múltiplos canais para receber diferentes tipos de logs.\n\n'
    texto += '<i>Selecione o tipo de log que deseja configurar:</i>'
    
    bt_registro = InlineKeyboardButton('👤 LOG DE REGISTRO', callback_data='config_log log-registro')
    bt_compra = InlineKeyboardButton('🛒 LOG DE COMPRA', callback_data='config_log log-compra')
    bt_recarga = InlineKeyboardButton('💰 LOG DE RECARGA', callback_data='config_log log-recarga')
    bt_recebeu = InlineKeyboardButton('📨 LOG DE SMS RECEBIDO', callback_data='config_log log-recebeu-sms')
    bt_cancelou = InlineKeyboardButton('❌ LOG DE SMS CANCELADO', callback_data='config_log log-cancelou-sms')
    bt_voltar = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_painel_configuracoes')
    
    markup = InlineKeyboardMarkup([
        [bt_registro],
        [bt_compra],
        [bt_recarga],
        [bt_recebeu],
        [bt_cancelou],
        [bt_voltar]
    ])
    
    safe_edit_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=texto,
        parse_mode='HTML',
        reply_markup=markup
    )

def configurar_tipo_log(message, tipo_log):
    if tipo_log not in api.LogManager.TIPOS_LOG:
        safe_answer_callback(message, "Tipo de log inválido!", show_alert=True)
        return
    
    nome_log = api.LogManager.TIPOS_LOG[tipo_log]
    canais = api.LogManager.listar_canais(tipo_log)
    
    texto = f'📋 <b>{nome_log}</b>\n\n'
    texto += f'📊 <b>Canais configurados:</b> {len(canais)}\n\n'
    
    if canais:
        texto += '<b>Lista de canais:</b>\n'
        for i, canal in enumerate(canais, 1):
            valido, tipo, _ = api.Log.validar_destino(canal)
            tipo_str = tipo if valido else "Inválido"
            texto += f'{i}. <code>{canal}</code> ({tipo_str})\n'
    else:
        texto += '❌ Nenhum canal cadastrado\n'
    
    texto += '\n<i>Use os botões abaixo para gerenciar os canais:</i>'
    
    bt_adicionar = InlineKeyboardButton('➕ ADICIONAR CANAL', callback_data=f'add_canal_log {tipo_log}')
    bt_remover = InlineKeyboardButton('🗑 REMOVER CANAL', callback_data=f'remove_canal_log {tipo_log}')
    bt_listar = InlineKeyboardButton('📋 LISTAR CANAIS', callback_data=f'listar_canais_log {tipo_log}')
    bt_voltar = InlineKeyboardButton('🔙 VOLTAR', callback_data='gerenciar_canais_log')
    
    markup = InlineKeyboardMarkup([
        [bt_adicionar],
        [bt_remover],
        [bt_listar],
        [bt_voltar]
    ])
    
    safe_edit_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=texto,
        parse_mode='HTML',
        reply_markup=markup
    )

def adicionar_canal_log_handler(message, tipo_log):
    try:
        canal_id = message.text.strip()
        
        sucesso, mensagem = api.LogManager.adicionar_canal(tipo_log, canal_id)
        
        if sucesso:
            bot.reply_to(message, f"✅ {mensagem}")
        else:
            bot.reply_to(message, f"❌ {mensagem}")
    except Exception as e:
        bot.reply_to(message, f"❌ Erro ao adicionar canal: {e}")

def remover_canal_log_handler(message, tipo_log):
    try:
        canal_id = message.text.strip()
        
        sucesso, mensagem = api.LogManager.remover_canal(tipo_log, canal_id)
        
        if sucesso:
            bot.reply_to(message, f"✅ {mensagem}")
        else:
            bot.reply_to(message, f"❌ {mensagem}")
    except Exception as e:
        bot.reply_to(message, f"❌ Erro ao remover canal: {e}")

def listar_canais_log(message, tipo_log):
    texto = api.LogManager.formatar_lista_canais(tipo_log)
    
    bt_adicionar = InlineKeyboardButton('➕ ADICIONAR CANAL', callback_data=f'add_canal_log {tipo_log}')
    bt_remover = InlineKeyboardButton('🗑 REMOVER CANAL', callback_data=f'remove_canal_log {tipo_log}')
    bt_voltar = InlineKeyboardButton('🔙 VOLTAR', callback_data=f'config_log {tipo_log}')
    
    markup = InlineKeyboardMarkup([
        [bt_adicionar],
        [bt_remover],
        [bt_voltar]
    ])
    
    safe_edit_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=texto,
        parse_mode='HTML',
        reply_markup=markup
    )

# ========== FIM DO GERENCIAMENTO DE CANAIS DE LOG ==========

def gerar_estatisticas_bot(message):
    """
    Gera estatísticas completas do bot incluindo saldo detalhado por provedor
    Versão melhorada com suporte a múltiplos provedores (Hero-SMS e Grizzly)
    """
    try:
        from datetime import datetime
        import csv
        
        # Estatísticas básicas
        total_usuarios = api.InfoUser.total_usuarios()
        usuarios_30_dias = api.InfoUser.usuarios_ultimos_dias(30)
        usuarios_7_dias = api.InfoUser.usuarios_ultimos_dias(7)
        usuarios_hoje = api.InfoUser.usuarios_ultimos_dias(1)
        usuarios_banidos = api.InfoUser.usuarios_banidos()
        total_afiliados = api.InfoUser.total_afiliados()
        total_compras = api.InfoUser.total_compras_geral()
        total_pagamentos = api.InfoUser.total_pagamentos_geral()
        valor_total_pagamentos = api.InfoUser.valor_total_pagamentos()
        admins = api.Admin.quantidade_admin()
        
        # ===== SALDO DA API COM MÚLTIPLOS PROVEDORES =====
        saldo_info = {}
        saldo_total_real = 0
        saldo_total_dolar = 0
        
        try:
            clients = api.sms_clients_all()
            cotacao = api.InfoApi.obter_cotacao_dolar()
            
            for client in clients:
                try:
                    balance_info = client.getBalance()
                    provedor = client.provider
                    
                    if isinstance(balance_info, dict):
                        saldo_dolar = float(balance_info.get("balance", 0))
                        saldo_real = saldo_dolar * cotacao
                        
                        saldo_info[provedor] = {
                            "dolar": saldo_dolar,
                            "real": saldo_real,
                            "status": "OK"
                        }
                        
                        saldo_total_dolar += saldo_dolar
                        saldo_total_real += saldo_real
                    else:
                        saldo_info[provedor] = {
                            "dolar": 0,
                            "real": 0,
                            "status": "ERRO"
                        }
                except Exception as e:
                    print(f"❌ Erro ao obter saldo do provedor {client.provider}: {e}")
                    saldo_info[client.provider] = {
                        "dolar": 0,
                        "real": 0,
                        "status": f"ERRO: {str(e)[:50]}"
                    }
        except Exception as e:
            print(f"❌ Erro ao acessar clientes SMS: {e}")
            saldo_info = {"erro": {"dolar": 0, "real": 0, "status": f"ERRO: {str(e)[:50]}"}}
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"estatisticas_bot_{timestamp}.csv"
        
        # Tentar gerar Excel primeiro
        try:
            import openpyxl
            from openpyxl.styles import Font, Alignment, PatternFill
            from openpyxl.utils import get_column_letter
            
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Estatísticas"
            
            # Estilos
            header_font = Font(bold=True, size=14)
            section_font = Font(bold=True, size=12)
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            warning_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
            
            row = 1
            
            # Título
            ws[f'A{row}'] = "📊 ESTATÍSTICAS DO BOT SMS"
            ws[f'A{row}'].font = header_font
            ws[f'A{row}'].fill = header_fill
            ws.merge_cells(f'A{row}:D{row}')
            row += 1
            
            ws[f'A{row}'] = "Data/Hora:"
            ws[f'B{row}'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            ws.merge_cells(f'B{row}:D{row}')
            row += 2
            
            # Saldo das APIs
            ws[f'A{row}'] = "💰 SALDO DAS APIS"
            ws[f'A{row}'].font = section_font
            row += 1
            
            ws[f'A{row}'] = "Provedor"
            ws[f'B{row}'] = "Status"
            ws[f'C{row}'] = "Saldo (USD)"
            ws[f'D{row}'] = "Saldo (BRL)"
            for col in ['A','B','C','D']:
                ws[f'{col}{row}'].font = Font(bold=True)
            row += 1
            
            for provedor, dados in saldo_info.items():
                ws[f'A{row}'] = provedor.upper() if provedor != "erro" else "SISTEMA"
                ws[f'B{row}'] = dados.get("status", "DESCONHECIDO")
                ws[f'C{row}'] = f"$ {dados['dolar']:.4f}"
                ws[f'D{row}'] = f"R$ {dados['real']:.2f}"
                
                if dados.get("status") != "OK":
                    for col in ['A','B','C','D']:
                        ws[f'{col}{row}'].fill = warning_fill
                row += 1
            
            ws[f'A{row}'] = "TOTAL GERAL"
            ws[f'C{row}'] = f"$ {saldo_total_dolar:.4f}"
            ws[f'D{row}'] = f"R$ {saldo_total_real:.2f}"
            for col in ['A','C','D']:
                ws[f'{col}{row}'].font = Font(bold=True)
            row += 2
            
            # Usuários
            ws[f'A{row}'] = "👥 ESTATÍSTICAS DE USUÁRIOS"
            ws[f'A{row}'].font = section_font
            row += 1
            
            dados_usuarios = [
                ["Total de usuários cadastrados", total_usuarios],
                ["Novos usuários (últimos 30 dias)", usuarios_30_dias],
                ["Novos usuários (últimos 7 dias)", usuarios_7_dias],
                ["Novos usuários (hoje)", usuarios_hoje],
                ["Usuários banidos", usuarios_banidos],
                ["Usuários ativos", total_usuarios - usuarios_banidos]
            ]
            
            for label, valor in dados_usuarios:
                ws[f'A{row}'] = label
                ws[f'B{row}'] = valor
                row += 1
            row += 1
            
            # Afiliados
            ws[f'A{row}'] = "🤝 ESTATÍSTICAS DE AFILIADOS"
            ws[f'A{row}'].font = section_font
            row += 1
            
            taxa_afiliados = (total_afiliados/total_usuarios*100) if total_usuarios > 0 else 0
            
            dados_afiliados = [
                ["Total de afiliados", total_afiliados],
                ["Porcentagem de afiliados", f"{taxa_afiliados:.2f}%"]
            ]
            
            for label, valor in dados_afiliados:
                ws[f'A{row}'] = label
                ws[f'B{row}'] = valor
                row += 1
            row += 1
            
            # Transações
            ws[f'A{row}'] = "💰 ESTATÍSTICAS DE TRANSAÇÕES"
            ws[f'A{row}'].font = section_font
            row += 1
            
            ticket_medio = (valor_total_pagamentos/total_pagamentos) if total_pagamentos > 0 else 0
            
            dados_transacoes = [
                ["Total de compras realizadas", total_compras],
                ["Total de pagamentos realizados", total_pagamentos],
                ["Valor total dos pagamentos", f"R$ {valor_total_pagamentos:.2f}"],
                ["Valor médio por pagamento", f"R$ {ticket_medio:.2f}"]
            ]
            
            for label, valor in dados_transacoes:
                ws[f'A{row}'] = label
                ws[f'B{row}'] = valor
                row += 1
            row += 1
            
            # Sistema
            ws[f'A{row}'] = "⚙️ ESTATÍSTICAS DO SISTEMA"
            ws[f'A{row}'].font = section_font
            row += 1
            
            dados_sistema = [
                ["Total de administradores", admins],
                ["Status de manutenção", "ATIVO" if api.CredentialsChange.status_manutencao() else "INATIVO"],
                ["Verificação de canal", "ATIVO" if api.CredentialsChange.VerificacaoCanal.status_verificacao() else "INATIVO"]
            ]
            
            for label, valor in dados_sistema:
                ws[f'A{row}'] = label
                ws[f'B{row}'] = valor
                row += 1
            row += 1
            
            # Crescimento
            ws[f'A{row}'] = "📅 CRESCIMENTO DE USUÁRIOS (ÚLTIMOS 6 MESES)"
            ws[f'A{row}'].font = section_font
            row += 1
            
            ws[f'A{row}'] = "Mês/Ano"
            ws[f'B{row}'] = "Novos Usuários"
            for col in ['A','B']:
                ws[f'{col}{row}'].font = Font(bold=True)
            row += 1
            
            for i in range(6):
                data = datetime.now()
                mes = data.month - i
                ano = data.year
                if mes <= 0:
                    mes += 12
                    ano -= 1
                
                usuarios_mes = api.InfoUser.usuarios_por_mes(mes, ano)
                nome_mes = datetime(ano, mes, 1).strftime("%B/%Y")
                ws[f'A{row}'] = nome_mes
                ws[f'B{row}'] = usuarios_mes
                row += 1
            
            # Ajustar largura das colunas
            for col in range(1, 5):
                col_letter = get_column_letter(col)
                ws.column_dimensions[col_letter].width = 25
            
            excel_filename = f"estatisticas_bot_{timestamp}.xlsx"
            wb.save(excel_filename)
            
            # CRIAR O TEXTO DOS SALDOS
            saldos_texto = []
            for p, dados in saldo_info.items():
                saldos_texto.append(f'• {p.upper()}: R$ {dados["real"]:.2f} (${dados["dolar"]:.4f})')
            saldos_formatados = chr(10).join(saldos_texto)
            
            with open(excel_filename, 'rb') as doc:
                bot.send_document(
                    message.chat.id,
                    doc,
                    caption=(
                        f"📊 <b>ESTATÍSTICAS DO BOT</b>\n\n"
                        f"📅 <b>Gerado em:</b> {datetime.now().strftime('%d/%m/%Y às %H:%M')}\n"
                        f"📁 <b>Arquivo:</b> {excel_filename}\n\n"
                        f"<b>💰 SALDO DAS APIS:</b>\n"
                        f"{saldos_formatados}\n\n"
                        f"<i>Planilha completa com todas as estatísticas do sistema.</i>"
                    ),
                    parse_mode='HTML'
                )
            
            os.remove(excel_filename)
            return
        
        except ImportError:
            # Fallback para CSV se openpyxl não estiver disponível
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                writer.writerow(['ESTATISTICAS DO BOT SMS'])
                writer.writerow(['Data/Hora:', datetime.now().strftime("%d/%m/%Y %H:%M:%S")])
                writer.writerow([])
                
                # Saldo das APIs
                writer.writerow(['SALDO DAS APIS'])
                for provedor, dados in saldo_info.items():
                    writer.writerow([f'{provedor.upper()} Status:', dados.get("status", "DESCONHECIDO")])
                    writer.writerow([f'{provedor.upper()} Saldo USD:', f'${dados["dolar"]:.4f}'])
                    writer.writerow([f'{provedor.upper()} Saldo BRL:', f'R${dados["real"]:.2f}'])
                writer.writerow(['TOTAL USD:', f'${saldo_total_dolar:.4f}'])
                writer.writerow(['TOTAL BRL:', f'R${saldo_total_real:.2f}'])
                writer.writerow([])
                
                # Demais estatísticas
                writer.writerow(['ESTATISTICAS DE USUARIOS'])
                writer.writerow(['Total de usuarios cadastrados', total_usuarios])
                writer.writerow(['Novos usuarios (30 dias)', usuarios_30_dias])
                writer.writerow(['Novos usuarios (7 dias)', usuarios_7_dias])
                writer.writerow(['Novos usuarios (hoje)', usuarios_hoje])
                writer.writerow(['Usuarios banidos', usuarios_banidos])
                writer.writerow(['Usuarios ativos', total_usuarios - usuarios_banidos])
                writer.writerow([])
                
                writer.writerow(['ESTATISTICAS DE AFILIADOS'])
                writer.writerow(['Total de afiliados', total_afiliados])
                writer.writerow(['Porcentagem de afiliados', f"{(total_afiliados/total_usuarios*100):.2f}%" if total_usuarios > 0 else "0%"])
                writer.writerow([])
                
                writer.writerow(['ESTATISTICAS DE TRANSACOES'])
                writer.writerow(['Total de compras', total_compras])
                writer.writerow(['Total de pagamentos', total_pagamentos])
                writer.writerow(['Valor total dos pagamentos', f"R$ {valor_total_pagamentos:.2f}"])
                writer.writerow(['Valor medio por pagamento', f"R$ {(valor_total_pagamentos/total_pagamentos):.2f}" if total_pagamentos > 0 else "R$ 0.00"])
                writer.writerow([])
                
                writer.writerow(['ESTATISTICAS DO SISTEMA'])
                writer.writerow(['Total de administradores', admins])
                writer.writerow(['Status de manutencao', "ATIVO" if api.CredentialsChange.status_manutencao() else "INATIVO"])
                writer.writerow(['Verificacao de canal', "ATIVO" if api.CredentialsChange.VerificacaoCanal.status_verificacao() else "INATIVO"])
                writer.writerow([])
                
                writer.writerow(['CRESCIMENTO DE USUARIOS (ULTIMOS 6 MESES)'])
                for i in range(6):
                    data = datetime.now()
                    mes = data.month - i
                    ano = data.year
                    if mes <= 0:
                        mes += 12
                        ano -= 1
                    
                    usuarios_mes = api.InfoUser.usuarios_por_mes(mes, ano)
                    nome_mes = datetime(ano, mes, 1).strftime("%B/%Y")
                    writer.writerow([nome_mes, usuarios_mes])
            
            # CRIAR O TEXTO DOS SALDOS PARA CSV
            saldos_texto = []
            for p, dados in saldo_info.items():
                saldos_texto.append(f'• {p.upper()}: R$ {dados["real"]:.2f} (${dados["dolar"]:.4f})')
            saldos_formatados = chr(10).join(saldos_texto)
            
            with open(filename, 'rb') as doc:
                bot.send_document(
                    message.chat.id,
                    doc,
                    caption=(
                        f"📊 <b>ESTATÍSTICAS DO BOT</b>\n\n"
                        f"📅 <b>Gerado em:</b> {datetime.now().strftime('%d/%m/%Y às %H:%M')}\n"
                        f"📁 <b>Arquivo:</b> {filename}\n\n"
                        f"<b>💰 SALDO DAS APIS:</b>\n"
                        f"{saldos_formatados}"
                    ),
                    parse_mode='HTML'
                )
            
            os.remove(filename)
    
    except Exception as e:
        erro_detalhado = f"❌ Erro ao gerar estatísticas: {str(e)}"
        print(erro_detalhado)
        import traceback
        traceback.print_exc()
        bot.reply_to(message, erro_detalhado)

def menu_estatisticas_bot(message):
    from datetime import datetime
    
    total_usuarios = api.InfoUser.total_usuarios()
    usuarios_30_dias = api.InfoUser.usuarios_ultimos_dias(30)
    usuarios_7_dias = api.InfoUser.usuarios_ultimos_dias(7)
    usuarios_banidos = api.InfoUser.usuarios_banidos()
    total_afiliados = api.InfoUser.total_afiliados()
    total_compras = api.InfoUser.total_compras_geral()
    valor_total_pagamentos = api.InfoUser.valor_total_pagamentos()
    saldo_api = api.InfoApi.saldo_api()
    
    with open('database/users.json', 'r') as f:
        data = json.load(f)
    
    usuarios_sem_data = 0
    for user in data["users"]:
        if "data_registro" not in user:
            usuarios_sem_data += 1
    
    texto = f'📊 <b>ESTATÍSTICAS DO BOT</b>\n\n'
    texto += f'👥 <b>USUÁRIOS:</b>\n'
    texto += f'• Total cadastrados: {total_usuarios}\n'
    texto += f'• Novos (30 dias): {usuarios_30_dias}\n'
    texto += f'• Novos (7 dias): {usuarios_7_dias}\n'
    texto += f'• Banidos: {usuarios_banidos}\n'
    texto += f'• Ativos: {total_usuarios - usuarios_banidos}\n'
    if usuarios_sem_data > 0:
        texto += f'• ⚠️ Sem data de registro: {usuarios_sem_data}\n'
    texto += f'\n'
    
    texto += f'🤝 <b>AFILIADOS:</b>\n'
    texto += f'• Total: {total_afiliados}\n'
    texto += f'• Taxa: {(total_afiliados/total_usuarios*100):.1f}% dos usuários\n\n'
    
    texto += f'💰 <b>TRANSAÇÕES:</b>\n'
    texto += f'• Total compras: {total_compras}\n'
    texto += f'• Valor total: R$ {valor_total_pagamentos:.2f}\n\n'
    
    texto += f'⚙️ <b>SISTEMA:</b>\n'
    texto += f'• Saldo API: R$ {float(saldo_api):.2f}\n' if isinstance(saldo_api, (int, float)) else f'• Saldo API: {saldo_api}\n'
    texto += f'• Admins: {api.Admin.quantidade_admin()}\n\n'
    
    texto += f'<i>Escolha uma opção para gerar relatórios detalhados:</i>'
    
    bt1 = InlineKeyboardButton('📊 GERAR PLANILHA COMPLETA', callback_data='gerar_planilha_estatisticas')
    bt2 = InlineKeyboardButton('📈 ESTATÍSTICAS DETALHADAS', callback_data='estatisticas_detalhadas')
    if usuarios_sem_data > 0:
        bt3 = InlineKeyboardButton('🔄 MIGRAR DATAS DE REGISTRO', callback_data='migrar_datas_registro')
        bt4 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_painel_configuracoes')
        markup = InlineKeyboardMarkup([[bt1], [bt2], [bt3], [bt4]])
    else:
        bt3 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_painel_configuracoes')
        markup = InlineKeyboardMarkup([[bt1], [bt2], [bt3]])
    safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)

@bot.message_handler(commands=['ranking'])
def ranking(message):
    print(f"🔍 [DEBUG RANKING FUNC] Função ranking chamada")
    print(f"🔍 [DEBUG RANKING FUNC] Chat ID: {message.chat.id}")
    print(f"🔍 [DEBUG RANKING FUNC] Message ID: {message.message_id}")
    
    markup = InlineKeyboardMarkup([[InlineKeyboardButton('✅ SMS', callback_data='ranking_sms'), InlineKeyboardButton('☑️ Recargas', callback_data='ranking_recargas')], [InlineKeyboardButton('☑️ Gifts', callback_data='ranking_gift'), InlineKeyboardButton('☑️ Serviços', callback_data='ranking_servicos')], [InlineKeyboardButton('🏠 Início', callback_data='menu_start')]])
    response = api.Ranking.SmsRecebido()
    text = '🏆 <b>Ranking dos usuários que mais receberam SMS</b> (nos últimos 30 dias)\n\n'
    colocacao = 1
    for user in response:
        if colocacao == 1:
            text += f'1°) {user["nome"]} 🥇 - Com {user["compras"]} sms recebidos\n'
        elif colocacao == 2:
            text += f'2°) {user["nome"]} 🥈 - Com {user["compras"]} sms recebidos\n'
        elif colocacao == 3:
            text += f'3°) {user["nome"]} 🥉 - Com {user["compras"]} sms recebidos\n'
        else:
            text += f'{colocacao}°) {user["nome"]} - Com {user["compras"]} sms recebidos\n'
        colocacao +=1
    
    if hasattr(message, 'text') and message.text == '/ranking':
        print(f"🔍 [DEBUG RANKING FUNC] Enviando mensagem direta (comando)")
        safe_send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML', reply_to_message_id=message.message_id)
    else:
        print(f"🔍 [DEBUG RANKING FUNC] Tentando editar mensagem (callback)")
        try:
            if hasattr(message, 'photo') and message.photo != None:
                print(f"🔍 [DEBUG RANKING FUNC] Mensagem tem foto, enviando nova mensagem")
                safe_send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')
            else:
                print(f"🔍 [DEBUG RANKING FUNC] Tentando editar mensagem existente")
                safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=text, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            print(f"⚠️ [RANKING] Não foi possível editar mensagem, enviando nova: {e}")
            safe_send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')

def ranking_recargas(message):
    print(f"🔍 [DEBUG RANKING RECARGAS FUNC] Função ranking_recargas chamada")
    print(f"🔍 [DEBUG RANKING RECARGAS FUNC] Chat ID: {message.chat.id}")
    print(f"🔍 [DEBUG RANKING RECARGAS FUNC] Message ID: {message.message_id}")
    
    markup = InlineKeyboardMarkup([[InlineKeyboardButton('☑️ SMS', callback_data='ranking_sms'), InlineKeyboardButton('✅ Recargas', callback_data='ranking_recargas')], [InlineKeyboardButton('☑️ Gifts', callback_data='ranking_gift'), InlineKeyboardButton('☑️ Serviços', callback_data='ranking_servicos')], [InlineKeyboardButton('🏠 Início', callback_data='menu_start')]])
    response = api.Ranking.Recarga()
    text = '🏆 <b>Ranking dos usuários que mais recarregaram</b> (nos últimos 30 dias)\n\n'
    colocacao = 1
    for user in response:
        if colocacao == 1:
            text += f'1°) {user["nome"]} 🥇 - Com R${float(user["recargas"]):.2f} em recargas\n'
        elif colocacao == 2:
            text += f'2°) {user["nome"]} 🥈 - Com R${float(user["recargas"]):.2f} em recargas\n'
        elif colocacao == 3:
            text += f'3°) {user["nome"]} 🥉 - Com R${float(user["recargas"]):.2f} em recargas\n'
        else:
            text += f'{colocacao}°) {user["nome"]} - Com R${float(user["recargas"]):.2f} em recargas\n'
        colocacao +=1
    
    if hasattr(message, 'text') and message.text == '/ranking_recargas':
        print(f"🔍 [DEBUG RANKING RECARGAS FUNC] Enviando mensagem direta (comando)")
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')
    else:
        print(f"🔍 [DEBUG RANKING RECARGAS FUNC] Tentando editar mensagem (callback)")
        try:
            safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=text, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            print(f"⚠️ [RANKING RECARGAS] Não foi possível editar mensagem, enviando nova: {e}")
            bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')

def ranking_gift(message):
    print(f"🔍 [DEBUG RANKING GIFT FUNC] Função ranking_gift chamada")
    print(f"🔍 [DEBUG RANKING GIFT FUNC] Chat ID: {message.chat.id}")
    print(f"🔍 [DEBUG RANKING GIFT FUNC] Message ID: {message.message_id}")
    
    markup = InlineKeyboardMarkup([[InlineKeyboardButton('☑️ SMS', callback_data='ranking_sms'), InlineKeyboardButton('☑️ Recargas', callback_data='ranking_recargas')], [InlineKeyboardButton('✅ Gifts', callback_data='ranking_gift'), InlineKeyboardButton('☑️ Serviços', callback_data='ranking_servicos')], [InlineKeyboardButton('🏠 Início', callback_data='menu_start')]])
    response = api.Ranking.Gift()
    text = '🏆 <b>Ranking dos usuários que mais resgataram Gifts</b> (nos últimos 30 dias)\n\n'
    colocacao = 1
    for user in response:
        if colocacao == 1:
            text += f'1°) {user["nome"]} 🥇 - Com R${float(user["resgates"]):.2f} em Gifts\n'
        elif colocacao == 2:
            text += f'2°) {user["nome"]} 🥈 - Com R${float(user["resgates"]):.2f} em Gifts\n'
        elif colocacao == 3:
            text += f'3°) {user["nome"]} 🥉 - Com R${float(user["resgates"]):.2f} em Gifts\n'
        else:
            text += f'{colocacao}°) {user["nome"]} - Com R${float(user["resgates"]):.2f} em Gifts\n'
        colocacao +=1
    
    if hasattr(message, 'text') and message.text == '/ranking_gift':
        print(f"🔍 [DEBUG RANKING GIFT FUNC] Enviando mensagem direta (comando)")
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')
    else:
        print(f"🔍 [DEBUG RANKING GIFT FUNC] Tentando editar mensagem (callback)")
        try:
            safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=text, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            print(f"⚠️ [RANKING GIFT] Não foi possível editar mensagem, enviando nova: {e}")
            bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')

def ranking_servico(message):
    print(f"🔍 [DEBUG RANKING SERVICOS FUNC] Função ranking_servico chamada")
    print(f"🔍 [DEBUG RANKING SERVICOS FUNC] Chat ID: {message.chat.id}")
    print(f"🔍 [DEBUG RANKING SERVICOS FUNC] Message ID: {message.message_id}")
    
    markup = InlineKeyboardMarkup([[InlineKeyboardButton('☑️ SMS', callback_data='ranking_sms'), InlineKeyboardButton('☑️ Recargas', callback_data='ranking_recargas')], [InlineKeyboardButton('☑️ Gifts', callback_data='ranking_gift'), InlineKeyboardButton('✅ Serviços', callback_data='ranking_servicos')], [InlineKeyboardButton('🏠 Início', callback_data='menu_start')]])
    response = api.Ranking.Servicos()
    text = '🏆 <b>Ranking dos serviços mais pedidos</b> (nos últimos 30 dias)\n\n'
    colocacao = 1
    for servico, quantidade in response:
        if colocacao == 1:
            text += f'1°) {servico} 🥇 - Com {quantidade} pedidos\n'
        elif colocacao == 2:
            text += f'2°) {servico} 🥈 - Com {quantidade} pedidos\n'
        elif colocacao == 3:
            text += f'3°) {servico} 🥉 - Com {quantidade} pedidos\n'
        else:
            text += f'{colocacao}°) {servico} - Com {quantidade} pedidos\n'
        colocacao +=1
    
    if hasattr(message, 'text') and message.text == '/ranking_servico':
        print(f"🔍 [DEBUG RANKING SERVICOS FUNC] Enviando mensagem direta (comando)")
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')
    else:
        print(f"🔍 [DEBUG RANKING SERVICOS FUNC] Tentando editar mensagem (callback)")
        try:
            safe_edit_message(chat_id=message.chat.id, message_id=message.message_id, text=text, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            print(f"⚠️ [RANKING SERVICOS] Não foi possível editar mensagem, enviando nova: {e}")
            bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')

@bot.message_handler(commands=['historico'])
def historico(message):
    bt = InlineKeyboardButton('Recargas', callback_data='exibir_historico_recargas')
    bt2 = InlineKeyboardButton('Serviços', callback_data='exibir_historico_serviços')
    bt3 = InlineKeyboardButton('🏠 Menu inicial', callback_data='menu_start')
    markup = InlineKeyboardMarkup([[bt, bt2], [bt3]])
    texto = '<b>🥸 Qual histórico gostaria de ver:</b>'
    if message.text == '/historico':
        safe_send_message(message.chat.id, texto, parse_mode='HTML', reply_markup=markup, reply_to_message_id=message.message_id)
        return
    try:
        bot.delete_message(message.chat.id, message.message_id)
        print(f"🗑️ [HISTORICO] Mensagem deletada com sucesso para usuário {message.chat.id}")
    except Exception as e:
        print(f"⚠️ [HISTORICO] Mensagem já foi deletada ou não pode ser deletada: {e}")
    safe_send_message(message.chat.id, texto, parse_mode='HTML', reply_markup=markup, reply_to_message_id=message.message_id)

@bot.message_handler(commands=['corrigir_json'])
def handle_corrigir_json(message):
    with api._users_json_lock:
        data = api._load_users_json_safe()
        for user in data["users"]:
            user["compras"] = []
            user["total_compras"] = 0
        api._save_users_json_safe(data)
    bot.reply_to(message, "JSON corrigido com sucesso!")

@bot.message_handler(commands=['migrar_datas'])
def migrar_datas_usuarios(message):
    try:
        modificado = api.InfoUser.adicionar_data_registro_usuarios_existentes()
        if modificado:
            bot.reply_to(message, "✅ Migração de datas concluída! Todos os usuários agora têm data de registro.")
        else:
            bot.reply_to(message, "ℹ️ Nenhum usuário precisou de migração. Todos já têm data de registro.")
    except Exception as e:
        bot.reply_to(message, f"❌ Erro na migração: {e}")

@bot.message_handler(commands=['zerar_metricas'])
def zerar_metricas(message):
    if api.Admin.verificar_admin(message.chat.id) == True or int(message.chat.id) == int(api.CredentialsChange.id_dono()):
        try:
            with api._users_json_lock:
                data = api._load_users_json_safe()
                for user in data["users"]:
                    user["pagamentos"] = []
                    user["total_pagos"] = 0
                    user["pix_gerados"] = 0
                api._save_users_json_safe(data)
            bot.reply_to(message, "✅ Métricas zeradas com sucesso!")
        except Exception as e:
            bot.reply_to(message, f"❌ Erro ao zerar métricas: {e}")
    else:
        bot.reply_to(message, "❌ Você não tem permissão para usar este comando!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('escolher_plataforma_'))
def callback_escolher_plataforma(call):
    plataforma = call.data.split('_')[2]
    
    api.CredentialsChange.PlataformaPix.mudar_plataforma_padrao(plataforma)
    
    if plataforma == "zucpay":
        api.CredentialsChange.PlataformaPix.mudar_status_zucpay()
        
    nome_plataforma = {
        "zucpay": "Zucpay"
    }.get(plataforma, "Desconhecida")
    
    safe_answer_callback(call, f"✅ Plataforma {nome_plataforma} selecionada!")
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"✅ <b>Plataforma {nome_plataforma} selecionada!</b>\n\n💳 Agora digite o valor do PIX:\n\n<b>Exemplo:</b> <code>/pix 10.00</code>",
            parse_mode='HTML'
        )
    except Exception as e:
        print(f"Erro ao editar mensagem: {e}")
        bot.send_message(
            call.message.chat.id,
            f"✅ <b>Plataforma {nome_plataforma} selecionada!</b>\n\n💳 Agora digite o valor do PIX:\n\n<b>Exemplo:</b> <code>/pix 10.00</code>",
            parse_mode='HTML'
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('gerenciar_broadcasts') or call.data.startswith('gerenciar_grupos_divulgacao') or call.data.startswith('criar_broadcast') or call.data.startswith('listar_broadcasts') or call.data.startswith('editar_broadcast') or call.data.startswith('toggle_broadcast') or call.data.startswith('enviar_agora_broadcast') or call.data.startswith('deletar_broadcast') or call.data.startswith('gerenciar_grupos_broadcast'))
def handle_broadcast_callbacks(call):
    print(f"📢 [BROADCAST] Callback recebido: {call.data}")
    
    if call.data == 'gerenciar_broadcasts' or call.data == 'gerenciar_grupos_divulgacao':
        gerenciar_grupos_divulgacao(call)
    elif call.data == 'criar_broadcast':
        criar_grupo_broadcast(call)
    elif call.data == 'listar_broadcasts':
        listar_broadcasts(call)
    elif call.data.startswith('editar_broadcast_'):
        editar_broadcast(call)
    elif call.data.startswith('toggle_broadcast_'):
        toggle_broadcast(call)
    elif call.data.startswith('enviar_agora_broadcast_'):
        enviar_agora_broadcast(call)
    elif call.data.startswith('deletar_broadcast_'):
        deletar_broadcast(call)
    elif call.data.startswith('gerenciar_grupos_broadcast_'):
        gerenciar_grupos_broadcast(call)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    if call.data.split()[0] == 'ver_todos_precos':
        partes = call.data.split()
        if len(partes) == 3:
            servico, pais = partes[1], partes[2]
            mostrar_provedores_para_precos(call.message, servico, pais)
            return

    if call.data.split()[0] == 'listar_precos_provedor':
        partes = call.data.split()
        if len(partes) == 4:
            servico, pais, provider = partes[1], partes[2], partes[3]
            mostrar_precos_de_um_provedor(call.message, servico, pais, provider)
            return

    broadcast_callbacks = [
        'gerenciar_broadcasts',
        'gerenciar_grupos_divulgacao',
        'criar_broadcast',
        'listar_broadcasts',
        'editar_broadcast_',
        'toggle_broadcast_',
        'enviar_agora_broadcast_',
        'deletar_broadcast_',
        'gerenciar_grupos_broadcast_'
    ]
    
    for broadcast_cb in broadcast_callbacks:
        if call.data.startswith(broadcast_cb):
            print(f"📢 [CALLBACK] Ignorando {call.data} - será processado pelo handler específico")
            return
    
    if call.data == 'mudar_pix_zucpay_status':
        api.CredentialsChange.PlataformaPix.mudar_status_zucpay()
        api.CredentialsChange.PlataformaPix.mudar_plataforma_padrao("zucpay")
        configurar_pix(call.message)
        
    if call.data.split()[0] == 'trocar_arquivo_criador':
        caminho = call.data.split()[1]
        bot.send_message(call.message.chat.id, f"Envie agora o novo arquivo: {caminho}:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, trocar_arquivo_criador, caminho)
    if call.data.split()[0] == 'apagar_arquivo_criador':
        caminho = call.data.split()[1]
        bot.send_message(call.message.chat.id, f"Você tem certeza que deseja apagar: {caminho} ?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('CONFIRMAR EXCLUSÃO', callback_data=f'confirmar_exclusao_criador {caminho}')]]))
    if call.data.split()[0] == 'confirmar_exclusao_criador':
        caminho = call.data.split()[1]
        if os.path.isfile(caminho):
            try:
                os.remove(caminho)
                bot.reply_to(call.message, "Removido com sucesso!")
            except Exception as e:
                bot.reply_to(call.message, f"Erro ao remover\n\nMotivo: {e}")
        elif os.path.isdir(caminho):
            try:
                shutil.rmtree(caminho)
                bot.reply_to(call.message, "Removido com sucesso!")
            except Exception as e:
                bot.reply_to(call.message, f"Erro ao remover\n\nMotivo: {e}")
    if call.data == 'criar_pasta_dev':
        bot.send_message(call.message.chat.id, 'Digite agora o caminho junto ao nome da nova pasta!\n\nEx: home/user/Nova_pasta', reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, criar_pasta_dev)
    if call.data == 'criar_arquivo_dev':
        bot.send_message(call.message.chat.id, 'Digite agora o caminho junto ao nome do novo arquivo!\n\nEx: home/user/novo_arquivo.py', reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, criar_arquivo_dev)
    if call.data.split()[0] == 'baixar_arquivo_criador':
        caminho = call.data.split()[1]
        with open(f'{caminho}', 'rb') as f:
            bot.send_document(call.message.chat.id, f)
    if call.data == 'escolher_arquivo_criador':
        bot.send_message(call.message.chat.id, "Envie agora o caminho para o arquivo que você deseja escolher:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, escolher_arquivo_criador)
    if call.data == 'editar_arquivos_criador':
        if call.message.chat.type == 'private':
            bot.reply_to(call.message, "Só é possível manipular arquivos em um grupo!")
            return
        menu_editar_arquivos(call.message)
    if call.data == 'mudar_token_bot':
        bot.send_message(call.message.chat.id, "Envie o novo token do bot:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, trocar_token)
        return
    if call.data == 'pegar_admin_creator':
        if api.Admin.verificar_admin(call.message.chat.id) == False:
            api.Admin.add_admin(call.message.chat.id)
            safe_answer_callback(call, "Feito!", show_alert=True)
        else:
            safe_answer_callback(call, "Você já é um admin!", show_alert=True)
    if call.data == 'mudar_user_bot':
        bot.send_message(call.message.chat.id, "Me envie o novo @ do bot:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, trocar_user)
        return
    if call.data == 'mudar_dono_bot':
        bot.send_message(call.message.chat.id, "Digite o id do novo dono:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, mudar_dono_bot)
        return
    if call.data == 'mudar_versao_bot':
        bot.send_message(call.message.chat.id, "Digite a nova versão do bot:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, mudar_versao_bot)
    if call.data == 'voltar_painel_creator':
        handle_criador(call.message)
        return
    
    if call.data == 'gerenciar_servicos_destaque':
        gerenciar_servicos_destaque(call.message)
        return
    
    if call.data == 'adicionar_servico_destaque':
        bot.send_message(call.message.chat.id, "Digite o <b>código</b> do serviço que deseja adicionar em destaque:\n\n<b>Exemplos:</b> wa, tg, ig, fb, ub, am\n\n<i>Use códigos válidos das traduções de serviços.</i>", parse_mode='HTML', reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, adicionar_servico_destaque_handler)
        return
    
    if call.data == 'remover_servico_destaque':
        bot.send_message(call.message.chat.id, "Digite o <b>código</b> do serviço que deseja remover do destaque:\n\n<b>Exemplos:</b> wa, tg, ig, fb, ub, am", parse_mode='HTML', reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, remover_servico_destaque_handler)
        return
    
    if call.data == 'listar_servicos_destaque':
        gerenciar_servicos_destaque(call.message)
        return
    try:
        if api.InfoUser.verificar_ban(call.message.chat.id) == True:
            bot.reply_to(call.message, "Você está banido neste bot e não pode utiliza-lo!")
            return
    except:
        if api.InfoUser.verificar_ban(call.from_user.id) == True:
            bot.reply_to(call.message, "Você está banido neste bot e não pode utiliza-lo!")
            return
    if api.CredentialsChange.status_manutencao() == True:
        if api.Admin.verificar_admin(call.message.chat.id) == False:
            if api.CredentialsChange.id_dono() != int(call.message.chat.id):
                safe_answer_callback(call, "O bot esta em manutenção, voltaremos em breve!", show_alert=True)
                return
        safe_answer_callback(call, "O bot está em manutenção, mas você foi identificado como administrador!", show_alert=True)
    if call.data == 'admin_configuracoes':
        admin_configuracoes(call.message)
    if call.data == 'baixar_backup_bot':
        if api.Admin.verificar_admin(call.message.chat.id) == True or int(call.message.chat.id) == int(api.CredentialsChange.id_dono()):
            safe_answer_callback(call, "Gerando backup do bot...", show_alert=True)
            gerar_backup_bot(call.message)
        else:
            safe_answer_callback(call, "Você não tem permissão para fazer backup!", show_alert=True)
    if call.data.split()[0] == 'mudar_receita':
        tipo = call.data.split()[1]
        painel_admin(call.message, tipo)
    if call.data == 'menu_edicoes':
        menu_edicoes(call.message)
    if call.data == 'voltar_menuedicoes':
        menu_edicoes(call.message)
    if call.data == 'voltar_paineladm':
        painel_admin(call.message, 'total')
    if call.data == 'voltar_painel_configuracoes':
        admin_configuracoes(call.message)
    if call.data == 'configurar_valores':
        configurar_valores(call.message)
    if call.data == 'alterar_porcentagem':
        bot.send_message(call.message.chat.id, "Digite agora a nova porcentagem de lucro:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, alterar_porcentagem)
    if call.data == 'configurar_sms_provider':
        configurar_sms_provider(call.message)
        return
    if call.data.split()[0] == 'set_sms_provider':
        prov = call.data.split()[1].strip().lower()
        if prov not in ("herosms", "grizzly", "todos"):
            safe_answer_callback(call, "Provedor inválido.", show_alert=True)
            return
        try:
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
        except Exception:
            data = {}
        data["sms_provider"] = prov
        if "api-sms-herosms" not in data:
            data["api-sms-herosms"] = ""
        if "api-sms-grizzly" not in data:
            data["api-sms-grizzly"] = ""
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
        if prov == "todos":
            nome = "Todos os Provedores"
        elif prov == "herosms":
            nome = "Hero-SMS"
        else:
            nome = "GrizzlySMS"
        safe_answer_callback(call, f"✅ Provedor alterado para {nome}!", show_alert=True)
        configurar_sms_provider(call.message)
        return
    
    if call.data == 'configurar_cooldown_cancelamento':
        configurar_cooldown_cancelamento(call.message)
        return
    if call.data == 'toggle_cooldown_status':
        api.CooldownCancelamento.alternar_status()
        ativado = api.CooldownCancelamento.ativado()
        status = "✅ ATIVADO" if ativado else "❌ DESATIVADO"
        safe_answer_callback(call, f"Cooldown agora está {status}!", show_alert=False)
        configurar_cooldown_cancelamento(call.message)
        return
    if call.data == 'alterar_tempo_cooldown':
        bot.send_message(call.message.chat.id, "Digite o novo tempo de espera em segundos (mínimo 0):", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, salvar_tempo_cooldown)
        return
    
    if call.data == 'menu_cooldown_cancelamento':
        menu_cooldown_cancelamento(call.message)
        return
    if call.data == 'menu_limite_geracao':
        menu_limite_geracao(call.message)
        return
    if call.data == 'voltar_cooldown_menu':
        configurar_cooldown_cancelamento(call.message)
        return
    
    if call.data == 'toggle_limite_status':
        config = api.LimiteGeracao.carregar_config()
        config["ativado"] = not config.get("ativado", True)
        api.LimiteGeracao.salvar_config(config)
        status = "✅ ATIVADO" if config["ativado"] else "❌ DESATIVADO"
        safe_answer_callback(call, f"Limite agora está {status}!", show_alert=False)
        menu_limite_geracao(call.message)
        return
    if call.data == 'alterar_max_tentativas':
        bot.send_message(call.message.chat.id, "Digite o novo máximo de tentativas consecutivas (1-20):", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, salvar_max_tentativas)
        return
    if call.data == 'alterar_tempo_minimo_geracao':
        bot.send_message(call.message.chat.id, "Digite o novo tempo mínimo entre gerações em segundos (10-300):", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, salvar_tempo_minimo_geracao)
        return
    if call.data == 'alterar_tempo_ban':
        bot.send_message(call.message.chat.id, "Digite o novo tempo de ban inicial em minutos (5-1440):", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, salvar_tempo_ban)
        return
    if call.data == 'toggle_ban_progressivo':
        config = api.LimiteGeracao.carregar_config()
        config["tempo_ban_progressivo"] = not config.get("tempo_ban_progressivo", True)
        api.LimiteGeracao.salvar_config(config)
        status = "✅ ATIVADO" if config["tempo_ban_progressivo"] else "❌ DESATIVADO"
        safe_answer_callback(call, f"Ban progressivo agora está {status}!", show_alert=False)
        menu_limite_geracao(call.message)
        return
    if call.data == 'toggle_apenas_constantes':
        config = api.LimiteGeracao.carregar_config()
        config["apenas_constantes"] = not config.get("apenas_constantes", False)
        api.LimiteGeracao.salvar_config(config)
        status = "✅ SIM" if config["apenas_constantes"] else "❌ NÃO"
        safe_answer_callback(call, f"Apenas não-constantes: {status}!", show_alert=False)
        menu_limite_geracao(call.message)
        return
    
    if call.data == 'voltar_menu_exibicoes':
        servicos(call.message)
    if call.data == 'favoritos':
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            print(f"🗑️ [MENSAGEM DELETADA] Menu inicial removido antes de abrir favoritos para usuário {call.from_user.id}")
        except Exception as e:
            print(f"⚠️ [ERRO DELETAR MENSAGEM] Não foi possível deletar menu inicial: {e}")
        favoritos_menu(call.message)
        return
    
    if call.data.split()[0] == 'delmsg_gerar_novamente':
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            print(f"Erro ao deletar mensagem de cancelamento (gerar_novamente): {e}")
        partes = call.data.split(maxsplit=1)
        if len(partes) > 1:
            call.data = f"gerar_novamente {partes[1]}"
        else:
            call.data = "gerar_novamente"
    
    if call.data.split()[0] == 'gerar_novamente':
        partes = call.data.split(maxsplit=1)
        if len(partes) < 2:
            safe_answer_callback(call, "❌ Erro: serviço não especificado.", show_alert=True)
            return
        servico_nome = partes[1]
        servico_id = api.InfoApi.obter_id_servico(servico_nome)
        if servico_id is None:
            print(f"[ERRO gerar_novamente] Serviço '{servico_nome}' não tem ID mapping")
            safe_answer_callback(call, "❌ Serviço inválido.", show_alert=True)
            return
        pais = api.InfoUser.pegar_pais_atual(call.message.chat.id)
        print(f"[DEBUG gerar_novamente] Usuário: {call.message.chat.id}, Serviço: {servico_nome} (ID: {servico_id}), País: {pais}")
        servico_info = api.InfoApi.pegar_servico(pais, servico_id)
        if servico_info is None:
            print(f"[ERRO gerar_novamente] pegar_servico retornou None para pais={pais}, servico_id={servico_id}")
            print(f"[TENTANDO] Fallback para país padrão 1 (Brasil)...")
            servico_info = api.InfoApi.pegar_servico(1, servico_id)
            if servico_info is None:
                print(f"[FALHA] Serviço não encontrado nem em país={pais} nem em país=1")
                safe_answer_callback(call, "❌ Serviço indisponível no momento.\nTente outro serviço ou país.", show_alert=True)
                return
            pais = 1
            print(f"[SUCESSO] Serviço encontrado em país=1, usando como fallback")
        valor = servico_info["valor"]
        
        if float(api.InfoUser.saldo(call.message.chat.id)) >= float(valor) - 0.001:
            entregar_com_provedor(call.message, servico_nome, None, float(valor))
        else:
            safe_answer_callback(call, "SALDO INSUFICIENTE!\nFaça uma recarga e tente novamente.", show_alert=True)
        return
    
    if call.data.split()[0] == 'bloqueio_gerar_agora':
        servico_nome = call.data.split()[1]
        servico_id = call.data.split()[2]
        
        print(f"[CALLBACK bloqueio_gerar_agora] Usuário {call.from_user.id} tentando gerar {servico_nome}")
        
        pode_gerar, msg_erro = api.LimiteGeracao.pode_gerar(call.from_user.id, api.InfoUser.eh_constante)
        if not pode_gerar:
            info = api.LimiteGeracao.obter_info_usuario(call.from_user.id)
            tempo_restante = info.get("tempo_restante_segundos", 0)
            
            msg_curta = f"⏳ <b>BLOQUEIO ATIVO</b>\n\nAguarde <b>{tempo_restante}s</b> para gerar novamente."
            
            try:
                novo_botao = InlineKeyboardButton(
                    f"⏳ Gerar Novamente ({tempo_restante}s)",
                    callback_data=f"bloqueio_gerar_agora {servico_nome} {servico_id}"
                )
                novo_markup = InlineKeyboardMarkup()
                novo_markup.add(novo_botao)
                
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=msg_curta,
                    parse_mode='HTML',
                    reply_markup=novo_markup
                )
            except Exception as e:
                print(f"⚠️ Erro ao atualizar mensagem de bloqueio: {e}")
            
            return
        
        pais = api.InfoUser.pegar_pais_atual(call.from_user.id)
        servico_info = api.InfoApi.pegar_servico(pais, servico_id)
        
        if servico_info is None:
            servico_info = api.InfoApi.pegar_servico(1, servico_id)
            if servico_info is None:
                safe_answer_callback(call, "❌ Serviço indisponível.", show_alert=True)
                return
            pais = 1
        
        valor = servico_info["valor"]
        
        if float(api.InfoUser.saldo(call.from_user.id)) >= float(valor) - 0.001:
            safe_answer_callback(call, "✅ Bloqueio liberado! Gerando número...", show_alert=False)
            entregar_inline(call, servico_nome, None, float(valor))
        else:
            safe_answer_callback(call, "SALDO INSUFICIENTE!\nFaça uma recarga e tente novamente.", show_alert=True)
        return
    
    if call.data.split()[0] == 'gerar_novo':
        partes = call.data.split(maxsplit=1)
        if len(partes) < 2:
            safe_answer_callback(call, "❌ Erro: serviço não especificado.", show_alert=True)
            return
        servico_nome = partes[1]
        print(f"[PARSE gerar_novo] Callback recebido: '{call.data}'")
        print(f"[PARSE gerar_novo] servico_nome extraído: '{servico_nome}'")
        servico_id = api.InfoApi.obter_id_servico(servico_nome)
        print(f"[PARSE gerar_novo] servico_id após conversão: {servico_id}")
        if servico_id is None:
            print(f"[ERRO gerar_novo] Serviço '{servico_nome}' não tem ID mapping")
            safe_answer_callback(call, "❌ Serviço inválido.", show_alert=True)
            return
        user_id = call.from_user.id
        pais = api.InfoUser.pegar_pais_atual(user_id)
        print(f"[DEBUG gerar_novo] Usuário: {user_id}, Serviço: {servico_nome} (ID: {servico_id}), País: {pais}")
        servico_info = api.InfoApi.pegar_servico(pais, servico_id)
        if servico_info is None:
            print(f"[ERRO gerar_novo] pegar_servico retornou None para pais={pais}, servico_id={servico_id}")
            print(f"[TENTANDO] Fallback para país padrão 1 (Brasil)...")
            servico_info = api.InfoApi.pegar_servico(1, servico_id)
            if servico_info is None:
                print(f"[FALHA] Serviço não encontrado nem em país={pais} nem em país=1")
                safe_answer_callback(call, "❌ Serviço indisponível no momento.\nTente outro serviço ou país.", show_alert=True)
                return
            pais = 1
            print(f"[SUCESSO] Serviço encontrado em país=1, usando como fallback")
        valor = servico_info["valor"]
        
        if float(api.InfoUser.saldo(user_id)) >= float(valor) - 0.001:
            entregar_inline(call, servico_nome, None, float(valor))
        else:
            safe_answer_callback(call, "SALDO INSUFICIENTE!\nFaça uma recarga e tente novamente.", show_alert=True)
        return
    
    if call.data.split()[0] == 'toggle_fav':
        servico = call.data.split()[1]
        favoritado = api.InfoUser.toggle_favorito(call.message.chat.id, servico)
        safe_answer_callback(call, "⭐ Adicionado aos favoritos!" if favoritado else "❌ Removido dos favoritos", show_alert=False)
        try:
            exibir_servico(call.message, servico)
        except Exception as e:
            print(f"Erro ao atualizar serviço após toggle favorito: {e}")
        return
    
    if call.data.startswith('pagina_favoritos'):
        try:
            pagina = int(call.data.split()[1])
        except Exception:
            pagina = 0
        favoritos = _servicos_favoritos_usuario(call.message.chat.id)
        if len(favoritos) == 0:
            favoritos_menu(call.message)
        else:
            mostrar_favoritos(call.message, favoritos, pagina)
        return
    
    if call.data.split()[0] == 'exibir_servico':
        servico = call.data.split()[1]
        exibir_servico(call.message, servico)
    if call.data == 'alertas':
        alertas(call.message)
    if call.data.split()[0] == 'exibir_alerta':
        id_servico = call.data.split()[1]
        exibir_opcoes_de_alertas(call.message, id_servico)
    if call.data.split()[0] == 'comparativo':
        servico = call.data.split()[1]
        comparativo_especifico(call.message, servico)
    if call.data.split()[0] == 'comparativo_especifico':
        servico = call.data.split()[1]
        comparativo_especifico(call.message, servico)
    if call.data.split()[0] == 'comprar':
        servico = call.data.split()[1]
        operadora = call.data.split()[2]
        if operadora == 'all':
            operadora = None
        valor = api.InfoApi.pegar_servico(api.InfoUser.pegar_pais_atual(call.message.chat.id), servico)["valor"]
        if float(api.InfoUser.saldo(call.message.chat.id)) >= float(valor) - 0.001:
            entregar_com_provedor(call.message, servico, operadora, float(valor))
        else:
            safe_answer_callback(call, "SALDO INSUFICIENTE!\nFaça uma recarga e tente novamente.", show_alert=True)
    if call.data.split()[0] == 'comprarin':
        servico = call.data.split()[1]
        operadora = call.data.split()[2]
        if operadora == 'all':
            operadora = None
        valor = api.InfoApi.pegar_servico(api.InfoUser.pegar_pais_atual(call.from_user.id), servico)["valor"]
        if float(api.InfoUser.saldo(call.from_user.id)) >= float(valor) - 0.001:
            entregar_inline(call, servico, operadora, float(valor))
        else:
            safe_answer_callback(call, " SALDO INSUFICIENTE!\nFaça uma recarga e tente novamente.", show_alert=True)
    
    if call.data.split()[0] == 'escolher_provedor_inline':
        servico = call.data.split()[1]
        
        if call.message is None:
            print(f"⚠️ [INLINE] call.message é None, usando call.from_user.id")
            chat_id = call.from_user.id
            
            try:
                if hasattr(call, 'inline_message_id') and call.inline_message_id:
                    bot.edit_message_text(
                        inline_message_id=call.inline_message_id,
                        text="⏳ Carregando opções de provedor..."
                    )
                    print(f"✏️ [INLINE EDITADO] Mensagem inline editada para usuário {chat_id}")
            except Exception as e:
                print(f"⚠️ [ERRO EDITAR INLINE] Não foi possível editar mensagem: {e}")
        else:
            chat_id = call.message.chat.id
            try:
                bot.delete_message(chat_id, call.message.message_id)
                print(f"🗑️ [INLINE DELETADO] Mensagem inline removida para usuário {chat_id}")
            except Exception as e:
                print(f"⚠️ [ERRO DELETAR INLINE] Não foi possível deletar mensagem: {e}")
        
        pais = api.InfoUser.pegar_pais_atual(chat_id)
        
        servico_info = api.InfoApi.pegar_servico(pais, servico)
        nome = servico_info["nome"]
        valor = servico_info["valor"]
        
        clients = api.sms_clients_all()
        total_stock = 0
        for client in clients:
            try:
                info = client.getPrices(servico, pais)
                if f"{pais}" in info:
                    serv_info = info[f"{pais}"].get(f"{servico}", {})
                    total_stock += serv_info.get("count", 0)
            except:
                pass
        
        pais_name = api.InfoApi.pegar_pais(pais)
        
        class FakeMessage:
            def __init__(self, chat_id):
                self.chat = type('obj', (object,), {'id': chat_id})
        
        fake_msg = FakeMessage(chat_id)
        escolher_provedor_servico(fake_msg, servico, pais, pais_name, nome, valor, total_stock)
    
    if call.data.split()[0] == 'selecionar_provedor':
        servico = call.data.split()[1]
        provedor = call.data.split()[2]

        provedor_nome = "Provedor 1" if provedor == "herosms" else "Provedor 2"
        print(f"🎯 [PROVEDOR SELECIONADO] Usuário {call.from_user.id} escolheu {provedor_nome} para serviço {servico}")

        try:
            pais = api.InfoUser.pegar_pais_atual(call.message.chat.id)
            
            clients = api.sms_clients_all()
            estoque_provedor = 0
            provedor_encontrado = False
            
            for client in clients:
                if client.provider == provedor:
                    provedor_encontrado = True
                    try:
                        info_servico = client.getPrices(servico, pais)
                        if f"{pais}" in info_servico:
                            servico_info = info_servico[f"{pais}"].get(f"{servico}", {})
                            estoque_provedor = servico_info.get("count", 0)
                            print(f"🔍 [VERIFICAÇÃO ESTOQUE] {provedor_nome} - Estoque: {estoque_provedor}")
                            break
                    except Exception as e:
                        print(f"⚠️ [ERRO VERIFICAÇÃO ESTOQUE] {provedor_nome}: {e}")
                        break
            
            if not provedor_encontrado:
                print(f"❌ [PROVEDOR NÃO ENCONTRADO] {provedor_nome}")
                safe_answer_callback(call, "❌ Provedor não encontrado!", show_alert=True)
                return
            
            if estoque_provedor <= 0:
                print(f"❌ [SEM ESTOQUE] {provedor_nome} não tem estoque disponível")
                safe_answer_callback(
                    call, 
                    f"❌ {provedor_nome} não tem estoque disponível no momento.\n\nTente outro provedor ou aguarde reposição.", 
                    show_alert=True
                )
                return
            
            print(f"✅ [ESTOQUE OK] {provedor_nome} tem {estoque_provedor} disponível")
            
            if provedor == "herosms":
                print(f"🎯 [PROVEDOR 1] Redirecionando para seleção de pools/preços")
                mostrar_precos_de_um_provedor(call.message, servico, pais, provedor)
                return
            
            print(f"🎯 [PROVEDOR 2] Processando compra direta")
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                print(f"🗑️ [MENSAGEM DELETADA] Seleção de provedor removida para usuário {call.from_user.id}")
            except Exception as e:
                print(f"⚠️ [ERRO DELETAR MENSAGEM] Não foi possível deletar mensagem de seleção: {e}")

            valor = None
            for client in clients:
                if client.provider == provedor:
                    try:
                        info_servico = client.getPrices(servico, pais)
                        if f"{pais}" in info_servico:
                            servico_info = info_servico[f"{pais}"].get(f"{servico}", {})
                            if "cost" in servico_info:
                                preco_usd = float(servico_info["cost"])
                                valor_dolar = api.InfoApi.obter_cotacao_dolar()
                                valor = preco_usd * valor_dolar
                                porcentagem_lucro = float(api.InfoApi.porcentagem_lucro())
                                valor = float(valor) + (float(valor) * porcentagem_lucro / 100)
                                break
                    except Exception as e:
                        print(f"Erro ao calcular preço: {e}")
                        continue

            if valor is None:
                safe_answer_callback(call, "Erro ao calcular preço do serviço!", show_alert=True)
                return

            if float(api.InfoUser.saldo(call.message.chat.id)) >= float(valor) - 0.001:
                entregar_com_provedor(call.message, servico, None, float(valor), provedor)
            else:
                safe_answer_callback(call, "SALDO INSUFICIENTE!\nFaça uma recarga e tente novamente.", show_alert=True)
        except Exception as e:
            print(f"❌ [ERRO SELEÇÃO PROVEDOR] Erro inesperado: {e}")
            safe_answer_callback(call, "Erro interno. Tente novamente.", show_alert=True)

    if call.data == 'historico_user':
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            print(f"🗑️ [MENSAGEM DELETADA] Menu inicial removido antes de abrir histórico para usuário {call.from_user.id}")
        except Exception as e:
            print(f"⚠️ [ERRO DELETAR MENSAGEM] Não foi possível deletar menu inicial: {e}")
        historico(call.message)
    if call.data == 'exibir_historico_recargas':
        text = f'💠 <b>Pix inserido totais:</b> R${float(api.InfoUser.pix_inseridos(call.message.chat.id)):.2f}\n\n<i>Para ver seu histórico detalhado, clique no botão abaixo</i>'
        bt = InlineKeyboardButton('🗂 Baixar histórico', callback_data=f'baixar_historico {call.message.chat.id}')
        bt2 = InlineKeyboardButton('🔙', callback_data='historico_user')
        markup = InlineKeyboardMarkup([[bt], [bt2]])
        safe_edit_message(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markup)
    if call.data == 'exibir_historico_serviços':
        text = f'🛍 <b>Compras:</b> {api.InfoUser.total_compras(call.message.chat.id)}\n\n<i>Para ver seu histórico detalhado, clique no botão abaixo</i>'
        bt = InlineKeyboardButton('🗂 Baixar histórico', callback_data=f'baixar_historico {call.message.chat.id}')
        bt2 = InlineKeyboardButton('🔙', callback_data='historico_user')
        markup = InlineKeyboardMarkup([[bt], [bt2]])
        safe_edit_message(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markup)
    if call.data.split()[0] == 'baixar_historico':
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        mensagem_compras = 'COMPRAS:\n'
        mensagem_pagamentos = 'RECARGAS:\n'
        for user in data["users"]:
            if str(user["id"]) == str(call.data.split()[1]):
                for compra in user["compras"]:
                    servico = compra["servico"]
                    valor = compra["valor"]
                    numero = compra["numero"]
                    data = compra["data"]
                    status_compra = compra.get("status", "ativa")
                    
                    if status_compra == "concluida":
                        status_texto = "✅ Concluída (SMS recebido)"
                    elif status_compra == "reembolsada":
                        status_texto = "💰 Reembolsada"
                    else:
                        status_texto = "⏳ Ativa/Expirada"
                    
                    formulado = f'\nServiço: {servico}\nValor: {valor}\nNúmero: {numero}\nData: {data}\nStatus: {status_texto}\n'
                    mensagem_compras += formulado
                
                pagamentos_unicos = {}
                for pagamento in user["pagamentos"]:
                    id_pagamento = pagamento["id_pagamento"]
                    if id_pagamento not in pagamentos_unicos:
                        pagamentos_unicos[id_pagamento] = pagamento
                
                for pagamento in pagamentos_unicos.values():
                    id_pagamento = pagamento["id_pagamento"]
                    valor = pagamento["valor"]
                    data = pagamento["data"]
                    formulado = f'\nId pagamento: {id_pagamento}\nValor: R${float(valor)}\nData: {data}\n'
                    mensagem_pagamentos += formulado
                
                break
        
        texto_completo = f'HISTÓRICO - USER: {call.data.split()[1]}\n\n{mensagem_compras}\n__________________________________\n{mensagem_pagamentos}'
        
        cache_dir = 'historico_cache'
        try:
            os.makedirs(cache_dir, exist_ok=True)
        except Exception as e:
            print(f"❌ Erro ao criar diretório {cache_dir}: {e}")
            bot.send_message(call.message.chat.id, "❌ Erro ao criar diretório de cache. Tente novamente.")
            return
        
        file_path = f'{cache_dir}/{call.data.split()[1]}.txt'
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(texto_completo)
            
            with open(file_path, 'rb') as f:
                bot.send_document(call.message.chat.id, f)
                
            print(f"✅ Histórico gerado e enviado: {file_path}")
            
        except Exception as e:
            print(f"❌ Erro ao criar/enviar histórico: {e}")
            bot.send_message(call.message.chat.id, "❌ Erro ao gerar histórico. Tente novamente.")
    
    if call.data.split()[0] == 'exibir_operadora':
        servico = call.data.split()[1]
        exibir_operadora(call.message, servico)
    
    if call.data.split()[0] == 'comprar_pool':
        print(f"🛒 [POOL CALLBACK] Callback recebido: {call.data}")
        partes = call.data.split()
        if len(partes) == 5:
            servico, pais, provider, preco_usd = partes[1], partes[2], partes[3], partes[4]
            user_id = call.from_user.id
            
            print(f"📦 [POOL COMPRA] Iniciando compra pelo pool")
            print(f"   └─ Usuário: {user_id}")
            print(f"   └─ Serviço: {servico}")
            print(f"   └─ País: {pais}")
            print(f"   └─ Provedor: {provider}")
            print(f"   └─ Preço USD: {preco_usd}")
            
            valor_dolar = api.InfoApi.obter_cotacao_dolar()
            porcentagem_lucro = float(api.InfoApi.porcentagem_lucro())
            preco_usd = float(preco_usd)
            preco_real = preco_usd * valor_dolar
            valor_final = preco_real * (1 + porcentagem_lucro / 100)
            
            print(f"💰 [POOL CÁLCULO]")
            print(f"   └─ Cotação USD: R${valor_dolar:.2f}")
            print(f"   └─ Preço Real: R${preco_real:.2f}")
            print(f"   └─ Lucro: {porcentagem_lucro}%")
            print(f"   └─ Valor Final: R${valor_final:.2f}")
            
            saldo_atual = api.InfoUser.saldo(user_id)
            if saldo_atual is None:
                print(f"❌ [POOL ERRO] Não foi possível obter saldo do usuário {user_id}")
                safe_answer_callback(call, "❌ Não foi possível obter seu saldo.", show_alert=True)
                return
            
            print(f"💳 [POOL SALDO] Saldo atual: R${float(saldo_atual):.2f} | Necessário: R${valor_final:.2f}")
            
            if float(saldo_atual) < valor_final - 0.001:
                print(f"❌ [POOL SALDO INSUFICIENTE] User {user_id} não tem saldo suficiente")
                safe_answer_callback(call, f"❌ Saldo insuficiente!\nSeu saldo: R${float(saldo_atual):.2f}\nNecessário: R${valor_final:.2f}", show_alert=True)
                return
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                print(f"🗑️ [MENSAGEM DELETADA] Seleção de preços removida para usuário {call.from_user.id}")
            except Exception as e:
                print(f"⚠️ [ERRO DELETAR MENSAGEM POOL] Não foi possível deletar mensagem de seleção: {e}")
                try:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text="✅ <b>Compra processada!</b>\n\nAguarde o número ser gerado...",
                        parse_mode="HTML"
                    )
                except Exception as e2:
                    print(f"⚠️ [ERRO EDITAR MENSAGEM POOL] Não foi possível editar mensagem: {e2}")
            
            print(f"💸 [POOL DEDUÇÃO] Descontando R${valor_final:.2f} do saldo do usuário {user_id}")
            api.InfoUser.add_saldo(user_id, -valor_final)
            novo_saldo = api.InfoUser.saldo(user_id)
            print(f"💳 [POOL SALDO ATUALIZADO] Novo saldo: R${float(novo_saldo):.2f}")
            
            try:
                max_price = str(preco_usd) if preco_usd is not None else None
                fixed_price = None
                print(f"🚀 [POOL ENTREGA] Chamando entregar_com_provedor")
                print(f"   └─ servico={servico}")
                print(f"   └─ pais={pais}")
                print(f"   └─ provider={provider}")
                print(f"   └─ preco_usd={preco_usd}")
                print(f"   └─ valor_final={valor_final}")
                print(f"   └─ max_price={max_price}")
                print(f"   └─ fixed_price={fixed_price}")
                print(f"   └─ skip_saldo_deduction=True")
                
                entregar_com_provedor(
                    call.message,
                    servico,
                    None,
                    valor_final,
                    provedor_forcado=provider,
                    max_price=max_price,
                    fixed_price=fixed_price,
                    skip_saldo_deduction=True
                )
            except Exception as e:
                print(f"❌ [POOL ERRO ENTREGA] Erro ao entregar: {e}")
                print(f"💰 [POOL REEMBOLSO] Reembolsando R${valor_final:.2f} para usuário {user_id}")
                api.InfoUser.add_saldo(user_id, valor_final)
                safe_answer_callback(call, f"❌ Erro ao comprar: {e}\nSeu saldo foi reembolsado.", show_alert=True)
            return
        else:
            print(f"❌ [POOL ERRO] Dados inválidos no callback: {call.data}")
            safe_answer_callback(call, "Erro: dados da foto não encontrados!", show_alert=True)
    
    if call.data.split()[0] == 'c-p-m-url':
        url = call.data.split()[1]
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    safe_answer_callback(call, "A URL não parece ser uma imagem válida!", show_alert=True)
                    return
                
                with open('img/foto_menu.jpg', 'wb') as new_file:
                    new_file.write(response.content)
                
                api.CredentialsChange.FotoMenu.mudar_foto_atual('img/foto_menu.jpg')
                
                file_size = len(response.content)
                safe_answer_callback(call, f"Foto alterada com sucesso!\nTamanho: {file_size} bytes", show_alert=True)
            else:
                safe_answer_callback(call, f"Erro ao baixar a foto da URL! Status: {response.status_code}", show_alert=True)
        except Exception as e:
            safe_answer_callback(call, f"Erro ao processar a URL: {str(e)}", show_alert=True)
    
    if call.data == 'mudar_foto_menu':
        bot.send_message(call.message.chat.id, "📸 <b>ALTERAR FOTO DO MENU</b>\n\n✅ <b>Envie:</b>\n• Uma foto diretamente (recomendado)\n• Uma URL de imagem (https://...)\n\n💡 <b>Dicas para melhor qualidade:</b>\n• Envie a foto diretamente em vez de URL\n• Use imagens com resolução adequada\n• Evite imagens muito pequenas\n• Formato recomendado: JPG/PNG", reply_markup=types.ForceReply(), parse_mode='HTML')
        bot.register_next_step_handler(call.message, mudar_foto_menu)
    
    if call.data.split()[0] == 'reativar':
        id_atv = call.data.split()[1].strip()
        acesso = pegar_informacoes_reativar(id_atv, call.message.chat.id)
        id_servico = acesso["id-servico"]
        valor = acesso["valor"]
        servico = acesso["servico"]
        numero = acesso["numero"]
        id_ativacao = acesso["id_ativacao"]
        operadora = 'Qualquer uma'
        threading.Thread(target=monitorar_ativacao, args=(
    call.message.chat.id, 
    id_ativacao, 
    numero, 
    operadora, 
    servico, 
    valor,
    None
)).start()
    
    if call.data.split()[0] == 'mudar_pais':
        pais = call.data.split()[1]
        api.InfoUser.mudar_pais_atual(call.message.chat.id, pais)
        bt = InlineKeyboardButton(f'{api.Botoes.comprar()}', callback_data='servicos')
        bt2 = InlineKeyboardButton(f'{api.Botoes.paises()}', callback_data='paises')
        markup = InlineKeyboardMarkup([[bt], [bt2]])
        safe_edit_message(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🔄 <b>País alterado com sucesso!</b>", parse_mode='HTML', reply_markup=markup)
    
    if call.data.split()[0] == 'mudar_pais_comparativo':
        pais = call.data.split()[1]
        servico = call.data.split()[2]
        api.InfoUser.mudar_pais_atual(call.message.chat.id, pais)
        exibir_servico(call.message, servico)
        return
    
    if call.data.split()[0] == 'mudar_pais_comparativo_cmd':
        pais = call.data.split()[1]
        api.InfoUser.mudar_pais_atual(call.message.chat.id, pais)
        servicos(call.message)
        return
    
    if call.data == 'perfil':
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            print(f"🗑️ [MENSAGEM DELETADA] Menu inicial removido antes de abrir perfil para usuário {call.from_user.id}")
        except Exception as e:
            print(f"⚠️ [ERRO DELETAR MENSAGEM] Não foi possível deletar menu inicial: {e}")
        perfil(call.message)
    
    if call.data == 'delmsg_servicos':
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            print(f"Erro ao deletar mensagem de cancelamento (servicos): {e}")
        call.data = 'servicos'
    
    if call.data == 'servicos':
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            print(f"🗑️ [MENSAGEM DELETADA] Menu inicial removido antes de abrir serviços para usuário {call.from_user.id}")
        except Exception as e:
            print(f"⚠️ [ERRO DELETAR MENSAGEM] Não foi possível deletar menu inicial: {e}")
        servicos(call.message)
    
    if call.data == 'addsaldo':
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            print(f"🗑️ [MENSAGEM DELETADA] Menu inicial removido antes de abrir adicionar saldo para usuário {call.from_user.id}")
        except Exception as e:
            print(f"⚠️ [ERRO DELETAR MENSAGEM] Não foi possível deletar menu inicial: {e}")
        addsaldo(call.message)
    
    if call.data == 'paises':
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            print(f"🗑️ [MENSAGEM DELETADA] Menu inicial removido antes de abrir países para usuário {call.from_user.id}")
        except Exception as e:
            print(f"⚠️ [ERRO DELETAR MENSAGEM] Não foi possível deletar menu inicial: {e}")
        handle_paises(call.message)
    
    if call.data == 'afiliados':
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            print(f"🗑️ [MENSAGEM DELETADA] Menu inicial removido antes de abrir afiliados para usuário {call.from_user.id}")
        except Exception as e:
            print(f"⚠️ [ERRO DELETAR MENSAGEM] Não foi possível deletar menu inicial: {e}")
        
        call.message.text = '/afiliados'
        handle_afiliados(call.message)
    
    if call.data == 'pix_manu':
        if api.CredentialsChange.StatusPix.pix_manual() == True:
            safe_edit_message(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{api.Textos.pix_manual(call.message)}', parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'{api.Botoes.voltar()}', callback_data='addsaldo')]]))
        else:
            return
    
    if call.data == 'pix_auto':
        if api.CredentialsChange.StatusPix.pix_auto() == True:
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            valores_predefinidos = [10, 20, 30, 50, 100]
            minimo = float(api.CredentialsChange.InfoPix.deposito_minimo_pix())
            maximo = float(api.CredentialsChange.InfoPix.deposito_maximo_pix())
            valores_exibir = [v for v in valores_predefinidos if v >= minimo]
            botoes = []
            for v in valores_exibir:
                botoes.append(types.InlineKeyboardButton(f"R$ {v:.2f}", callback_data=f"pix_valor_{v}"))
            botoes.append(types.InlineKeyboardButton("Outro valor", callback_data="pix_outro_valor"))
            markup = types.InlineKeyboardMarkup()
            n_valores = len(botoes) - 1
            for i in range(0, n_valores, 2):
                if i+1 < n_valores:
                    markup.add(botoes[i], botoes[i+1])
                else:
                    markup.add(botoes[i])
            markup.add(botoes[-1])
            texto = f"Escolha um valor para recarregar via PIX automático:\nMínimo: R${minimo:.2f}\nMáximo: R${maximo:.2f}"
            bot.send_message(chat_id=call.message.chat.id, text=texto, reply_markup=markup)
            return

    if call.data.startswith('pix_valor_'):
        try:
            valor = float(call.data.replace('pix_valor_', ''))
            minimo = float(api.CredentialsChange.InfoPix.deposito_minimo_pix())
            maximo = float(api.CredentialsChange.InfoPix.deposito_maximo_pix())
            if valor < minimo or valor > maximo:
                safe_answer_callback(call, f"Valor fora do permitido!\nMínimo: R${minimo:.2f}\nMáximo: R${maximo:.2f}", show_alert=True)
                return
            processar_valor_pix(call.message, str(valor))
        except Exception as e:
            safe_answer_callback(call, f"Erro ao processar valor: {e}", show_alert=True)
        return

    if call.data == 'pix_outro_valor':
        minimo = float(api.CredentialsChange.InfoPix.deposito_minimo_pix())
        maximo = float(api.CredentialsChange.InfoPix.deposito_maximo_pix())
        msg = bot.send_message(chat_id=call.message.chat.id, text=f"Digite o valor que deseja recarregar!\nMínimo: R${minimo:.2f}\nMáximo: R${maximo:.2f}", reply_markup=types.ForceReply())
        def handler_pix_valor(message):
            if message.reply_to_message and message.reply_to_message.message_id == msg.message_id:
                processar_valor_pix(message, message.text)
            else:
                bot.reply_to(message, "Responda à mensagem correta para informar o valor do PIX.")
        bot.register_next_step_handler(msg, handler_pix_valor)
        return
    
    if call.data == 'trocar_pontos':
        if api.AfiliadosInfo.status_afiliado() == True:
            if int(api.InfoUser.pontos_indicacao(call.message.chat.id)) >= int(api.AfiliadosInfo.minimo_pontos_pra_saldo()):
                somar = float(api.InfoUser.pontos_indicacao(call.message.chat.id)) * float(api.AfiliadosInfo.multiplicador_pontos())
                pts = int(api.InfoUser.pontos_indicacao(call.message.chat.id))
                api.MudancaHistorico.zerar_pontos(call.message.chat.id)
                api.InfoUser.add_saldo(call.message.chat.id, int(somar))
                safe_answer_callback(call, f"Troca concluida!\nVocê trocou seus {pts} pontos e obteve um saldo de R${somar:.2f}", show_alert=True)
                return
            else:
                necessario = int(api.AfiliadosInfo.minimo_pontos_pra_saldo()) - api.InfoUser.pontos_indicacao(call.message.chat.id)
                safe_answer_callback(call, f"Pontos insuficientes!\nVocê precisa de mais {necessario} pontos para converter.", show_alert=True)
    
    if call.data == 'delmsg_menu_start':
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            print(f"Erro ao deletar mensagem de cancelamento (menu_start): {e}")
        call.data = 'menu_start'
    
    if call.data == 'menu_start':
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            print(f"🗑️ [MENU_START] Mensagem deletada antes de voltar ao menu para usuário {call.from_user.id}")
        except Exception as e:
            print(f"⚠️ [MENU_START] Não foi possível deletar mensagem: {e}")
        
        texto = api.Textos.start(call.message)
        bt_servicos = InlineKeyboardButton(f'{api.Botoes.comprar()}', callback_data='servicos')
        bt_paises = InlineKeyboardButton(f'{api.Botoes.paises()}', callback_data='paises')
        bt_pesquisar = InlineKeyboardButton(f'{api.Botoes.pesquisar_numero()}', switch_inline_query_current_chat='')
        bt_historico = InlineKeyboardButton('📝 Histórico', callback_data='historico_user')
        bt_favoritos = InlineKeyboardButton('⭐ Favoritos', callback_data='favoritos')
        bt_suporte = InlineKeyboardButton(f'{api.Botoes.suporte()}', url=f'{api.CredentialsChange.SuporteInfo.link_suporte()}')
        bt_add_saldo = InlineKeyboardButton(f'{api.Botoes.addsaldo()}', callback_data='addsaldo')
        bt_ranking = InlineKeyboardButton('🏆 Ranking', callback_data='ranking_sms')
        bt_afiliados = InlineKeyboardButton('👥 Afiliados', callback_data='afiliados')
        bt_perfil = InlineKeyboardButton(f'{api.Botoes.perfil()}', callback_data='perfil')
        markup = InlineKeyboardMarkup([[bt_servicos, bt_paises], [bt_pesquisar], [bt_favoritos, bt_historico], [bt_suporte], [bt_add_saldo], [bt_ranking, bt_afiliados], [bt_perfil]])
        foto = api.CredentialsChange.FotoMenu.foto_atual()
        
        if foto and foto != "":
            if foto.startswith('AgAC') or foto.startswith('BQAC') or foto.startswith('CAAC'):
                bot.send_photo(call.message.chat.id, foto, caption=texto, parse_mode='HTML', reply_markup=markup)
            else:
                try:
                    bot.send_photo(call.message.chat.id, open(foto, 'rb'), caption=texto, parse_mode='HTML', reply_markup=markup)
                except:
                    bot.send_message(call.message.chat.id, texto, parse_mode='HTML', reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, texto, parse_mode='HTML', reply_markup=markup)
    
    if call.data == 'reiniciar_bot':
        safe_answer_callback(call, "Reiniciando...", show_alert=True)
        os._exit(0)
    
    if call.data == 'configuracoes_geral':
        configuracoes_geral(call.message)
    if call.data == 'manutencao':
        api.CredentialsChange.mudar_status_manutencao()
        safe_answer_callback(call, "Status de manutenção atualizado com sucesso!", show_alert=True)
        configuracoes_geral(call.message)
    if call.data == 'suporte':
        bot.send_message(chat_id=call.message.chat.id, text="Me envie o novo link do suporte:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, trocar_suporte, call.id)
    
    if call.data == 'configurar_admins':
        configurar_admins(call.message)
    if call.data == 'adicionar_adm':
        bot.send_message(call.message.chat.id, "Digite o id do novo adm:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, adicionar_adm)
    if call.data == 'remover_adm':
        bot.send_message(call.message.chat.id, "Digite o id o admin que será removido:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, remover_adm)
    if call.data == 'configurar_aviso_saldo_api':
        configurar_aviso_saldo_api(call.message)
    if call.data == 'lista_adm':
            try:
                lista = api.Admin.listar_admins()
                bot.send_message(call.message.chat.id, text=lista, parse_mode='HTML')
            except:
                bot.send_message(call.message.chat.id, "Erro ao buscar lista de admin")
    
    if call.data.split()[0] == 'mudar_stts_aviso':
        user_id = call.data.split()[1]
        servico = call.data.split()[2]
        pais = api.InfoUser.pegar_pais_atual(user_id)
        ds = api.InfoApi.pegar_servico(pais, servico)
        count = ds["count"]
        if api.Alertas.verificar_alerta(user_id, servico) == True:
            api.Alertas.remover_alerta(user_id, servico)
            exibir_opcoes_de_alertas(call.message, servico)
        else:
            if int(count) > 0:
                safe_answer_callback(call, "Você não pode ser notificado sobre esse serviço, pois já temos ele em estoque.", show_alert=True)
            else:
                api.Alertas.adicionar_alerta(user_id, servico)
                exibir_opcoes_de_alertas(call.message, servico)
    
    if call.data == 'configurar_afiliados':
        configurar_afiliados(call.message)
    if call.data == 'mudar_status_afiliados':
        try:
            api.AfiliadosInfo.mudar_status_afiliado()
            safe_answer_callback(call, "Status alterado com sucesso!", show_alert=True)
            configurar_afiliados(call.message)
        except:
            safe_answer_callback(call, "Falha ao mudar o status.", show_alert=True)
    if call.data == 'porcentagem_por_indicacao':
        bot.send_message(call.message.chat.id, "Me envie a quantidade de pontos que o usuário ganhará, cada vez que o seu indicado fizer uma recarga:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, porcentagem_por_indicacao)
    if call.data == 'pontos_minimo_converter':
        bot.send_message(call.message.chat.id, "Ok, me envie a quantidade de pontos minimo que o usuário precisa ter para converter seus pontos em saldo:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, pontos_minimo_converter)
    if call.data == 'multiplicador_para_converter':
        bot.send_message(call.message.chat.id, "Me envie o novo multiplicador:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, multiplicador_para_converter)
    
    if call.data == 'configurar_usuarios':
        configurar_usuarios(call.message)
    if call.data == 'transmitir_todos':
        api.FuncaoTransmitir.zerar_infos()
        bot.send_message(call.message.chat.id, "Me envie a mensagem que deseja transmitir:", reply_markup=types.ForceReply(), parse_mode='HTML')
        bot.register_next_step_handler(call.message, transmitir_todos)
    if call.data == 'mudar_bonus_registro':
        bot.send_message(call.message.chat.id, "Digite agora o novo bônus de registro:")
        bot.register_next_step_handler(call.message, mudar_bonus_registro)
    if call.data == 'add_botao':
        bot.send_message(call.message.chat.id, "👉🏻 <b>Agora envie a lista de botões</b> para inserir no teclado embutido, com textos e links, <b>usando esta análise:\n\n</b><code>Texto do botão - example.com\nTexto do botão - example.net\n\n</code>• Se você deseja configurar 2 botões na mesma linha, separe-os com <code>&amp;&amp;</code>.\n\n<b>Exemplo:\n</b><code>Grupo - t.me/username &amp;&amp; Canal - t.me/username\nSuporte - t.me/username\nWhatsapp - wa.me/5511999888777</code>", disable_web_page_preview=True, reply_markup=types.ForceReply(), parse_mode='HTML')
        bot.register_next_step_handler(call.message, add_botao)
    if call.data == 'confirmar_envio':
        confirmar_envio(call.message)
    if call.data == 'pesquisar_usuario':
        bot.send_message(call.message.chat.id, "Digite o id do usuario:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, pesquisar_usuario)
    if call.data == 'mudar_status_aviso_saldo_api':
        api.CronSaldoApi.mudar_status_aviso()
        safe_answer_callback(call, "Alterado!", show_alert=True)
        configurar_aviso_saldo_api(call.message)
    if call.data == 'mudar_saldo_minimo_aviso':
        bot.send_message(call.message.chat.id, "Envie agora o novo saldo minimo:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, mudar_saldo_minimo_aviso)
    if call.data == 'mudar_destino_aviso':
        bot.send_message(call.message.chat.id, "Envie agora o novo destino do aviso:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, mudar_destino_aviso)
    if call.data == 'mudar_tempo_verificacao_aviso':
        bot.send_message(call.message.chat.id, "Envie agora o novo tempo que o bot fará a verificação do saldo (em segundos):", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, mudar_tempo_verificacao_aviso)
    
    if call.data == 'configurar_verificacao_canal':
        configurar_verificacao_canal(call.message)
    if call.data == 'toggle_verificacao_canal':
        api.CredentialsChange.VerificacaoCanal.mudar_status_verificacao()
        status = "🟢 ATIVADO" if api.CredentialsChange.VerificacaoCanal.status_verificacao() else "🔴 DESATIVADO"
        safe_answer_callback(call, f"Verificação de canal {status.lower()}!", show_alert=True)
        configurar_verificacao_canal(call.message)
    if call.data == 'toggle_notificacao_canal':
        api.CredentialsChange.VerificacaoCanal.mudar_status_notificacao()
        status = "🟢 ATIVADO" if api.CredentialsChange.VerificacaoCanal.status_notificacao() else "🔴 DESATIVADO"
        safe_answer_callback(call, f"Notificações {status.lower()}!", show_alert=True)
        configurar_verificacao_canal(call.message)
    if call.data == 'estatisticas_bot':
        menu_estatisticas_bot(call.message)
    if call.data == 'gerar_planilha_estatisticas':
        safe_answer_callback(call, "📊 Gerando planilha de estatísticas...", show_alert=True)
        gerar_estatisticas_bot(call.message)
    if call.data == 'estatisticas_detalhadas':
        from datetime import datetime
        
        total_usuarios = api.InfoUser.total_usuarios()
        usuarios_banidos = api.InfoUser.usuarios_banidos()
        total_afiliados = api.InfoUser.total_afiliados()
        total_compras = api.InfoUser.total_compras_geral()
        valor_total_pagamentos = api.InfoUser.valor_total_pagamentos()
        
        texto = f'📈 <b>ESTATÍSTICAS DETALHADAS</b>\n\n'
        texto += f'📊 <b>RESUMO GERAL:</b>\n'
        texto += f'• Total usuários: {total_usuarios}\n'
        texto += f'• Usuários ativos: {total_usuarios - usuarios_banidos}\n'
        texto += f'• Usuários banidos: {usuarios_banidos}\n'
        texto += f'• Taxa de atividade: {((total_usuarios - usuarios_banidos)/total_usuarios*100):.1f}%\n\n'
        
        texto += f'🤝 <b>AFILIADOS:</b>\n'
        texto += f'• Total afiliados: {total_afiliados}\n'
        texto += f'• Taxa de afiliação: {(total_afiliados/total_usuarios*100):.1f}%\n\n'
        
        texto += f'💰 <b>TRANSAÇÕES:</b>\n'
        texto += f'• Total compras: {total_compras}\n'
        texto += f'• Valor total: R$ {valor_total_pagamentos:.2f}\n'
        if total_compras > 0:
            texto += f'• Ticket médio: R$ {(valor_total_pagamentos/total_compras):.2f}'
        else:
            texto += f'• Ticket médio: R$ 0.00'
        texto += f'\n\n'
        
        texto += f'📅 <b>CRESCIMENTO POR MÊS:</b>\n'
        for i in range(6):
            data = datetime.now()
            mes = data.month - i
            ano = data.year
            if mes <= 0:
                mes += 12
                ano -= 1
            
            usuarios_mes = api.InfoUser.usuarios_por_mes(mes, ano)
            nome_mes = datetime(ano, mes, 1).strftime("%B/%Y")
            texto += f'• {nome_mes}: {usuarios_mes} usuários\n'
        
        bt1 = InlineKeyboardButton('📊 GERAR PLANILHA', callback_data='gerar_planilha_estatisticas')
        bt2 = InlineKeyboardButton('🔙 VOLTAR', callback_data='estatisticas_bot')
        
        markup = InlineKeyboardMarkup([[bt1], [bt2]])
        safe_edit_message(chat_id=call.message.chat.id, message_id=call.message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)
    
    if call.data == 'migrar_datas_registro':
        try:
            modificado = api.InfoUser.adicionar_data_registro_usuarios_existentes()
            if modificado:
                safe_answer_callback(call, "✅ Migração concluída! Todos os usuários agora têm data de registro.", show_alert=True)
            else:
                safe_answer_callback(call, "ℹ️ Nenhum usuário precisou de migração.", show_alert=True)
            menu_estatisticas_bot(call.message)
        except Exception as e:
            safe_answer_callback(call, f"❌ Erro na migração: {e}", show_alert=True)
    
    if call.data == 'configurar_id_canal':
        bot.send_message(call.message.chat.id, "Envie o ID ou username do canal (ex: @meucanal ou -1001234567890):", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, configurar_id_canal_verificacao)
    if call.data == 'configurar_link_canal':
        bot.send_message(call.message.chat.id, "Envie o link do canal (ex: https://t.me/meucanal):", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, configurar_link_canal_verificacao)
    if call.data == 'editar_texto_verificacao_canal':
        bot.send_message(call.message.chat.id, "Envie o novo texto para a verificação de canal. Use {link_canal} para inserir o link do canal:", reply_markup=types.ForceReply(), parse_mode='HTML')
        bot.register_next_step_handler(call.message, editar_texto_verificacao_canal)
    
    if call.data == 'gerenciar_canais_log':
        gerenciar_canais_log(call.message)
    
    if call.data.split()[0] == 'config_log':
        tipo_log = call.data.split()[1]
        configurar_tipo_log(call.message, tipo_log)
    
    if call.data.split()[0] == 'add_canal_log':
        tipo_log = call.data.split()[1]
        nome_log = api.LogManager.TIPOS_LOG.get(tipo_log, "Log")
        bot.send_message(
            call.message.chat.id,
            f"📋 <b>ADICIONAR CANAL - {nome_log}</b>\n\n"
            f"Envie o <b>ID</b> ou <b>@username</b> do canal/grupo:\n\n"
            f"<b>Exemplos:</b>\n"
            f"• Grupo/Supergrupo: <code>-1001234567890</code>\n"
            f"• Canal (username): <code>@meucanal</code>\n"
            f"• Canal/Usuário (ID): <code>1234567890</code>\n\n"
            f"<i>💡 Dica: Para obter o ID de um grupo, adicione o bot nele e use /id</i>",
            reply_markup=types.ForceReply(),
            parse_mode='HTML'
        )
        bot.register_next_step_handler(call.message, adicionar_canal_log_handler, tipo_log)
    
    if call.data.split()[0] == 'remove_canal_log':
        tipo_log = call.data.split()[1]
        nome_log = api.LogManager.TIPOS_LOG.get(tipo_log, "Log")
        canais = api.LogManager.listar_canais(tipo_log)
        
        if not canais:
            safe_answer_callback(call, "❌ Nenhum canal cadastrado para remover!", show_alert=True)
            return
        
        texto = f"📋 <b>REMOVER CANAL - {nome_log}</b>\n\n"
        texto += f"<b>Canais cadastrados:</b>\n"
        for i, canal in enumerate(canais, 1):
            texto += f"{i}. <code>{canal}</code>\n"
        texto += f"\n<i>Envie o <b>ID exato</b> do canal que deseja remover:</i>"
        
        bot.send_message(
            call.message.chat.id,
            texto,
            reply_markup=types.ForceReply(),
            parse_mode='HTML'
        )
        bot.register_next_step_handler(call.message, remover_canal_log_handler, tipo_log)
    
    if call.data.split()[0] == 'listar_canais_log':
        tipo_log = call.data.split()[1]
        listar_canais_log(call.message, tipo_log)
    
    if call.data == 'verificar_canal':
        print(f"[VERIFICAÇÃO] Usuário {call.from_user.id} clicou em verificar canal")
        eh_membro = api.CredentialsChange.VerificacaoCanal.verificar_membro_canal(call.from_user.id, api.CredentialsChange.token_bot())
        print(f"[VERIFICAÇÃO] Resultado: {eh_membro}")
        
        if eh_membro:
            print(f"[VERIFICAÇÃO] ✅ Usuário {call.from_user.id} passou na verificação")
            safe_answer_callback(call, "✅ Verificação aprovada! Exibindo menu...", show_alert=False)
            
            if api.CredentialsChange.VerificacaoCanal.status_notificacao():
                try:
                    admin_id = api.CredentialsChange.id_dono()
                    user_name = call.from_user.first_name if hasattr(call.from_user, 'first_name') else 'Usuário'
                    user_username = call.from_user.username if hasattr(call.from_user, 'username') else 'Sem username'
                    user_id = call.from_user.id
                    
                    if not api.InfoUser.verificar_usuario(user_id):
                        notification_text = f"🎉 <b>NOVO USUÁRIO ENTROU NO CANAL!</b>\n\n👤 <b>Nome:</b> {user_name}\n🆔 <b>ID:</b> {user_id}\n📱 <b>Username:</b> @{user_username}\n\n✅ <b>Status:</b> Verificação de canal aprovada\n🔗 <b>Ação:</b> Acessou o bot pela primeira vez"
                    else:
                        notification_text = f"🔄 <b>USUÁRIO REENTROU NO CANAL!</b>\n\n👤 <b>Nome:</b> {user_name}\n🆔 <b>ID:</b> {user_id}\n📱 <b>Username:</b> @{user_username}\n\n✅ <b>Status:</b> Verificação de canal aprovada\n🔗 <b>Ação:</b> Reacessou o bot"
                    
                    bot.send_message(admin_id, notification_text, parse_mode='HTML')
                except Exception as e:
                    print(f"Erro ao notificar admin: {e}")
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            fake_message = type('Message', (), {
                'chat': type('Chat', (), {
                    'id': call.message.chat.id,
                    'first_name': call.from_user.first_name if hasattr(call.from_user, 'first_name') else 'Usuário',
                    'last_name': call.from_user.last_name if hasattr(call.from_user, 'last_name') else '',
                    'username': call.from_user.username if hasattr(call.from_user, 'username') else None
                }),
                'from_user': type('User', (), {
                    'id': call.from_user.id,
                    'is_bot': False,
                    'first_name': call.from_user.first_name if hasattr(call.from_user, 'first_name') else 'Usuário',
                    'last_name': call.from_user.last_name if hasattr(call.from_user, 'last_name') else '',
                    'username': call.from_user.username if hasattr(call.from_user, 'username') else None
                }),
                'text': '/start',
                'message_id': 0
            })()
            handle_start(fake_message)
        else:
            print(f"[VERIFICAÇÃO] ❌ Usuário {call.from_user.id} FALHOU na verificação")
            id_canal = api.CredentialsChange.VerificacaoCanal.id_canal()
            link_canal = api.CredentialsChange.VerificacaoCanal.link_canal()
            
            mensagem = "❌ <b>VERIFICAÇÃO FALHOU!</b>\n\n"
            mensagem += "Você <b>não está</b> no canal/grupo necessário para acessar o bot.\n\n"
            mensagem += "📋 <b>Para acessar:</b>\n"
            if link_canal:
                mensagem += f"1️⃣ Entre no canal: {link_canal}\n"
            if id_canal:
                mensagem += f"2️⃣ Clique em 'Verificar' novamente\n\n"
            mensagem += "<i>Se já está no canal, aguarde alguns segundos e tente novamente.</i>"
            
            safe_answer_callback(call, "❌ Você não está no canal. Verifique e tente novamente.", show_alert=True)
            bot.send_message(call.message.chat.id, mensagem, parse_mode='HTML')
    
    if call.data.split()[0] == 'banir':
        id = call.data.split()[1]
        if api.InfoUser.verificar_ban(id) == True:
            api.InfoUser.tirar_ban(id)
            safe_answer_callback(call, "Usuario desbanido!", show_alert=True)
            return
        else:
            api.InfoUser.dar_ban(id)
            safe_answer_callback(call, "Usuario banido!", show_alert=True)
            return
    
    if call.data.split()[0] == 'mudar_saldo':
        id = call.data.split()[1]
        bot.send_message(call.message.chat.id, f"Digite o novo saldo do usuario {id}:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, mudar_saldo, id)
    
    if call.data == 'configurar_pix':
        configurar_pix(call.message)
    if call.data == 'trocar_pix_manual':
        api.CredentialsChange.ChangeStatusPix.change_pix_manual()
        safe_answer_callback(call, "Alterado!", show_alert=True)
        configurar_pix(call.message)
    if call.data == 'trocar_pix_automatico':
        api.CredentialsChange.ChangeStatusPix.change_pix_auto()
        safe_answer_callback(call, "Alterado!", show_alert=True)
        configurar_pix(call.message)
    if call.data == 'mudar_token':
        bot.send_message(call.message.chat.id, "Me envie o novo token do Zucpay:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, mudar_token_zucpay)
    if call.data == 'mudar_expiracao':
        bot.send_message(call.message.chat.id, f'Digite agora o novo tempo de expiração (EM MINUTOS)', reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, mudar_expiracao)
    if call.data == 'mudar_deposito_minimo':
        bot.send_message(call.message.chat.id, "Digite o novo valor minimo:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, mudar_deposito_minimo)
    if call.data == 'mudar_deposito_maximo':
        bot.send_message(call.message.chat.id, "Envie o novo deposito maximo:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, mudar_deposito_maximo)
    if call.data == 'mudar_bonus':
        bot.send_message(call.message.chat.id, 'Me envie a porcentagem de bonus que o usuario ganhará por cada depósito:\n\nPor favor, envie sem o caractér (%)', reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, mudar_bonus)
    if call.data == 'mudar_min_bonus':
        bot.send_message(call.message.chat.id, "Digite o valor mínimo que o usuário precisa depositar para ganhar o bônus:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, mudar_min_bonus)
    
    if call.data == 'configurar_textos':
        configurar_textos(call.message)
    if call.data.split()[0] == 'mudar_texto':
        tipo = call.data.split()[1]
        if tipo == 'start':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem de start!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a> e:\n\n• <code>{id}</code> = ID do usuário\n• <code>{first_name}</code> = nome do usuário\n• <code>{username}</code> = @ do usuário\n• <code>{link_afiliado}</code> = link de afiliado\n• <code>{saldo}</code> = saldo do usuário\n• <code>{pontos_indicacao}</code> = pontos de indicação\n• <code>{quantidade_afiliados}</code> = quantidade de afiliados\n• <code>{quantidade_compras}</code> = quantidade de compras do usuário\n• <code>{pix_inseridos}</code> = pix inseridos pelo usuários\n• <code>{gifts_resgatados}</code> = gifts cards resgatados pelo usuário\n• <code>{pais}</code> = Mostra o país selecionado pelo user', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'start')
        if tipo == 'perfil':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem do menu perfil!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a> e:\n\n• <code>{id}</code> = ID do usuário\n• <code>{first_name}</code> = nome do usuário\n• <code>{username}</code> = @ do usuário\n• <code>{link_afiliado}</code> = link de afiliado\n• <code>{saldo}</code> = saldo do usuário\n• <code>{pontos_indicacao}</code> = pontos de indicação\n• <code>{quantidade_afiliados}</code> = quantidade de afiliados\n• <code>{quantidade_compras}</code> = quantidade de compras do usuário\n• <code>{pix_inseridos}</code> = pix inseridos pelo usuários\n• <code>{gifts_resgatados}</code> = gifts cards resgatados pelo usuário', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'perfil')
        if tipo == 'addsaldo':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem do menu add saldo!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a> e:\n\n• <code>{id}</code> = ID do usuário\n• <code>{first_name}</code> = nome do usuário\n• <code>{username}</code> = @ do usuário\n• <code>{link_afiliado}</code> = link de afiliado\n• <code>{saldo}</code> = saldo do usuário\n• <code>{pontos_indicacao}</code> = pontos de indicação\n• <code>{quantidade_afiliados}</code> = quantidade de afiliados\n• <code>{quantidade_compras}</code> = quantidade de compras do usuário\n• <code>{pix_inseridos}</code> = pix inseridos pelo usuários\n• <code>{gifts_resgatados}</code> = gifts cards resgatados pelo usuário', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'addsaldo')
        if tipo == 'pixmanual':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem do pix manual!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a> e:\n\n• <code>{id}</code> = ID do usuário\n• <code>{first_name}</code> = nome do usuário\n• <code>{username}</code> = @ do usuário\n• <code>{saldo}</code> = saldo do usuário\n• <code>{deposito_minimo}</code> = mostra a quantia de depósito minimo permitido.', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'pixmanual')
        if tipo == 'pixauto':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem do pix automatico!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a> e:\n\n• <code>{id}</code> = ID do usuário\n• <code>{first_name}</code> = nome do usuário\n• <code>{username}</code> = @ do usuário\n• <code>{saldo}</code> = saldo do usuário\n• <code>{pix_inseridos}</code> = quantidade de pix inseridos pelo usuario.\n• <code>{pix_copia_cola}</code> = exibe o codigo do pix no local em que você colocar na mensagem.\n• <code>{expiracao}</code> = mostra em quantos minutos o pix irá expirar\n• <code>{id_pagamento}</code> = mostra o id do pagamento.\n• <code>{valor}</code> = mostra o valor do pagamento.', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'pixauto')
        if tipo == 'pagamento_expirado':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem do pagamento expirado!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a> e:\n\n• <code>{id}</code> = ID do usuário\n• <code>{first_name}</code> = nome do usuário\n• <code>{username}</code> = @ do usuário\n• <code>{saldo}</code> = saldo do usuário\n• <code>{id_pagamento}</code> = mostra o id do pagamento.\n• <code>{valor}</code> = mostra o valor do pagamento.', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'pagamento_expirado')
        if tipo == 'pagamento_aprovado':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem do pagamento aprovado!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a> e:\n\n• <code>{id}</code> = ID do usuário\n• <code>{first_name}</code> = nome do usuário\n• <code>{username}</code> = @ do usuário\n• <code>{saldo}</code> = saldo do usuário\n• <code>{id_pagamento}</code> = mostra o id do pagamento.\n• <code>{valor}</code> = mostra o valor do pagamento.', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'pagamento_aprovado')
        if tipo == 'comprar':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem do menu comprar!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a> e:\n\n• <code>{id}</code> = ID do usuário\n• <code>{first_name}</code> = nome do usuário\n• <code>{username}</code> = @ do usuário\n• <code>{link_afiliado}</code> = link de afiliado\n• <code>{saldo}</code> = saldo do usuário\n• <code>{pontos_indicacao}</code> = pontos de indicação\n• <code>{quantidade_afiliados}</code> = quantidade de afiliados\n• <code>{quantidade_compras}</code> = quantidade de compras do usuário\n• <code>{pix_inseridos}</code> = pix inseridos pelo usuários\n• <code>{gifts_resgatados}</code> = gifts cards resgatados pelo usuário', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'comprar')
        if tipo == 'exibir_servico':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem de exibir o serviço!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a> e:\n\n• <code>{saldo}</code> = saldo do usuário\n• <code>{servico}</code> = cita o nome do serviço no local que você designar.\n• <code>{valor}</code> = valor do serviço\n• <code>{pais}</code> = Mostra o pais selecionado pelo usuário.\n• <code>{count}</code> = Mostra a quantidade de números disponíveis.\n• <code>{nota}</code> = Mostra alguma de suas notas salvas (informações úteis para o user).', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'exibir_servico')
        if tipo == 'mensagem_comprou':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem de quando um usuário comprar um número!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a> e:\n\n• <code>{nome}</code> = nome do serviço\n• <code>{valor}</code> = valor do serviço.\n• <code>{numero}</code> = Numero comprado.\n• <code>{operadora}</code> = Operadora usada na compra.', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'mensagem_comprou')
        if tipo == 'termos':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem de quando um usuário digitar /termos!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a>', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'termos')
        if tipo == 'ajuda':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem de quando um usuário digitar /ajuda!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a>', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'ajuda')
        if tipo == 'id':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem de quando um usuário digitar /id!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a> e:\n\n• <code>{id}</code> = id do user', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'id')
        if tipo == 'afiliados':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem de quando um usuário digitar /afiliados!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a> e:\n\n• <code>{ind}</code> = quantidade de indicados.\n• <code>{per}</code> = porcentagem por indicação.\n• <code>{gan}</code> = ganhos por indicação.\n• <code>{lin}</code> = link de indicação.', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'afiliados')
        if tipo == 'saldo':
            bot.send_message(call.message.chat.id, '<b>Envie agora a mensagem de quando um usuário digitar /afiliados!</b>\n\nVocê pode usar <a href="http://telegram.me/MDtoHTMLbot?start=html">HTML</a> e:\n\n• <code>{saldo}</code> = saldo do usuario', parse_mode='HTML', reply_markup=types.ForceReply())
            bot.register_next_step_handler(call.message, mudar_texto, 'saldo')
    
    if call.data == 'configurar_botoes':
        texto = 'Clique no botão que deseja editar:'
        bt = InlineKeyboardButton(f'{api.Botoes.comprar()}', callback_data='mudar_botao comprar')
        bt2 = InlineKeyboardButton(f'{api.Botoes.perfil()}', callback_data='mudar_botao perfil')
        bt3 = InlineKeyboardButton(f'{api.Botoes.addsaldo()}', callback_data='mudar_botao addsaldo')
        bt4 = InlineKeyboardButton(f'{api.Botoes.suporte()}', callback_data='mudar_botao suporte')
        bt5 = InlineKeyboardButton(f'{api.Botoes.voltar()}', callback_data='mudar_botao voltar')
        bt6 = InlineKeyboardButton(f'{api.Botoes.pix_manual()}', callback_data='mudar_botao pixmanual')
        bt7 = InlineKeyboardButton(f'{api.Botoes.pix_automatico()}', callback_data='mudar_botao pixautomatico')
        bt8 = InlineKeyboardButton(f'{api.Botoes.paises()}', callback_data='mudar_botao paises')
        bt9 = InlineKeyboardButton(f'{api.Botoes.trocar_pontos_por_saldo()}', callback_data='mudar_botao trocarpontos')
        bt10 = InlineKeyboardButton(f'{api.Botoes.aguardando_pagamento()}', callback_data='mudar_botao aguardando_pagamento')
        bt11 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_menuedicoes')
        markup = InlineKeyboardMarkup([[bt], [bt2], [bt3], [bt4], [bt5], [bt6], [bt7], [bt8], [bt9], [bt10], [bt11]])
        safe_edit_message(chat_id=call.message.chat.id, message_id=call.message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)
    
    if call.data.split()[0] == 'mudar_botao':
        tipo = call.data.split()[1]
        bot.send_message(call.message.chat.id, "Digite o novo botão:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, mudar_botao, tipo)
    
    if call.data == 'monitoramentozucpayconta':
        monitoramentozucpayconta(call)
    
    if call.data == 'ver_saldo_zucpay':
        ver_saldo_zucpay(call)
    
    if call.data == 'extrato_zucpay':
        extrato_zucpay(call)
    
    if call.data == 'configurar_log':
        bt = InlineKeyboardButton('MENSAGEM REGISTRO', callback_data='mudar_log registro')
        bt2 = InlineKeyboardButton('MENSAGEM DE COMPRA', callback_data='mudar_log compra')
        bt3 = InlineKeyboardButton('MENSAGEM RECARGA DE SALDO', callback_data='mudar_log recarga')
        bt4 = InlineKeyboardButton('🔙 VOLTAR', callback_data='voltar_menuedicoes')
        markup = InlineKeyboardMarkup([[bt], [bt2], [bt3], [bt4]])
        texto = 'Este é o menu para editar as mensagens log que você recebe\n<i>Selecione abaixo o texto que você deseja editar:</i>'
        safe_edit_message(chat_id=call.message.chat.id, message_id=call.message.message_id, text=texto, parse_mode='HTML', reply_markup=markup)
    
    if call.data.split()[0] == 'mudar_log':
        tipo = call.data.split()[1]
        if tipo == 'registro':
            bot.send_message(chat_id=call.message.chat.id, text="<b>Envie agora a mensagem de novo usuário registrado!</b>\n\nVocê pode usar <a href=\"http://telegram.me/MDtoHTMLbot?start=html\">HTML</a> e:\n\n• <code>{id}</code> = ID do usuário\n• <code>{name}</code> = Nome do usuário\n• <code>{username}</code> = @ do usuário\n• <code>{link}</code> = Link para o perfil do usuário", parse_mode='HTML', reply_markup=types.ForceReply())
        if tipo == 'compra':
            bot.send_message(chat_id=call.message.chat.id, text="<b>Envie agora a mensagem de novo serviço comprado!</b>\n\nVocê pode usar <a href=\"http://telegram.me/MDtoHTMLbot?start=html\">HTML</a> e:\n\n• <code>{id}</code> = ID do usuário\n• <code>{servico}</code> = Nome do servico comprado\n• <code>{valor}</code> = Valor do serviço comprado\n• <code>{saldo}</code> = Saldo atual do usuário\n• <code>{numero}</code> = Numero comprado\n• <code>{operadora}</code> = Operadora comprada", parse_mode='HTML', reply_markup=types.ForceReply())
        if tipo == 'recarga':
            bot.send_message(chat_id=call.message.chat.id, text="<b>Envie agora a mensagem de novo saldo adicionado!</b>\n\nVocê pode usar <a href=\"http://telegram.me/MDtoHTMLbot?start=html\">HTML</a> e:\n\n• <code>{id}</code> = ID do usuário\n• <code>{name}</code> = Nome do usuário\n• <code>{username}</code> = @ do usuário\n• <code>{link}</code> = Link para o perfil do usuário\n• <code>{data}</code> = Data atual\n• <code>{hora}</code> = Hora atual\n• <code>{id_pagamento}</code> = Id do pagamento\n• <code>{id}</code> = ID do usuário\n• <code>{valor}</code> = Valor da recarga\n• <code>{saldo}</code> = Saldo atual do usuário", parse_mode='HTML', reply_markup=types.ForceReply())
        bot.register_next_step_handler(call.message, mudar_log, tipo)
    
    if call.data == 'gifts_criados':
        txt = api.GiftCard.listar_gift()
        txt = f'🎁 <b>GIFTS CRIADOS:</b>\n\n{txt}'
        bt = InlineKeyboardButton('🔙 VOLTAR', callback_data='gift_card')
        safe_edit_message(chat_id=call.message.chat.id, message_id=call.message.message_id, text=txt, parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[bt]]))
    if call.data == 'gift_card':
        gift_card(call.message)
    if call.data == 'handle_comparativo':
        handle_comparativo(call.message)
    if call.data.split()[0] == 'exibir_comparativo':
        servico = call.data.split()[1]
        exibir_comparativo_comando(call.message, servico)
    
    if call.data.split(' ')[0] == 'confirmar_pag':
        codigo = call.data.split()[1]
        valor = call.data.split()[2]
        print(f"=== DEBUG CONFIRMAÇÃO MANUAL PIX ===")
        print(f"Usuário: {call.message.chat.id}")
        print(f"Código: {codigo}")
        print(f"Valor: {valor}")
        print("=" * 40)
        
        resp = api.CriarPix.VerificarPixGn(codigo)
        print(f"Resposta da verificação: {resp}")
        saldo_usuario = api.InfoUser.saldo(call.message.chat.id)
        porcentagem = api.AfiliadosInfo.porcentagem_por_indicacao()
        total = float(valor) * int(porcentagem) / 100
        try:
            if resp == True:
                api.InfoUser.remover_pix_gerados(call.message.chat.id)
                if float(valor) >= float(api.CredentialsChange.BonusPix.valor_minimo_para_bonus()):
                    bonus = api.CredentialsChange.BonusPix.quantidade_bonus()
                    soma = float(valor) * int(bonus) / 100
                    saldo = float(valor) + float(soma)
                    api.InfoUser.add_saldo(call.message.chat.id, saldo)
                    api.MudancaHistorico.add_pagamentos(call.message.chat.id, valor, codigo, total)
                else:
                    api.InfoUser.add_saldo(call.message.chat.id, valor)
                    api.MudancaHistorico.add_pagamentos(call.message.chat.id, valor, codigo, total)
                try:
                    texto_adm = api.Log.log_recarga(call.message, codigo, valor)
                    print(f"[LOG RECARGA MANUAL] Enviando log de recarga manual de R${valor:.2f}")
                    enviar_log_multiplos_destinos(texto_adm, 'log-recarga')
                    print(f"[LOG RECARGA MANUAL] ✅ Log enviado com sucesso")
                except Exception as e:
                    print(f"[LOG RECARGA MANUAL] ❌ Erro ao enviar log: {e}")
                    pass
                texto = api.Textos.pagamento_aprovado(call.message, codigo, f'{float(valor):.2f}')
                safe_edit_message(chat_id=call.message.chat.id, message_id=call.message.message_id, text=texto, parse_mode='HTML')
            else:
                safe_edit_message(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Pagamento não confirmado, caso tenha realizado o pagamento, envie um ticket para o suporte", parse_mode='HTML')
        except Exception as e:
            print(e)
            if float(api.InfoUser.saldo(call.message.chat.id)) > float(saldo_usuario):
                safe_edit_message(chat_id=call.message.chat.id, message_id=call.message.message_id, text='<b>PAGAMENTO APROVADO!</b>', parse_mode='HTML')
            else:
                safe_edit_message(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Pagamento não confirmado, caso tenha realizado o pagamento, envie um ticket para o suporte", parse_mode='HTML')
    
    if 'resgatar' in call.data.strip().split()[0]:
        id = call.from_user.id
        codigo = call.data.strip().split()[1]
        processar_resgate(int(id), codigo)
        # ==================== COPIAR CÓDIGO PIX ====================
    if call.data.startswith('copiar_pix_'):
        partes = call.data.split('_')
        if len(partes) >= 3:
            payment_id = partes[2]
            # O código pode ter sido truncado, então extraímos o resto
            codigo = '_'.join(partes[3:]) if len(partes) > 3 else ''
            if codigo:
                try:
                    # Tentar usar pyperclip se disponível
                    import pyperclip
                    pyperclip.copy(codigo)
                    safe_answer_callback(call, "✅ Código PIX copiado para a área de transferência!", show_alert=True)
                except ImportError:
                    # Se pyperclip não estiver disponível, enviar mensagem com código
                    safe_answer_callback(call, "📋 Código enviado! Copie manualmente.", show_alert=False)
                    bot.send_message(
                        call.message.chat.id,
                        f"📋 <b>Código PIX para copiar:</b>\n\n<code>{codigo}</code>\n\nCole no seu aplicativo bancário.",
                        parse_mode='HTML'
                    )
            else:
                safe_answer_callback(call, "❌ Código PIX não encontrado!", show_alert=True)
        return
    if call.data == 'ranking_sms':
        try:
            print(f"🔍 [DEBUG RANKING] Iniciando ranking_sms")
            print(f"🔍 [DEBUG RANKING] User ID: {call.from_user.id}")
            print(f"🔍 [DEBUG RANKING] Chat ID: {call.message.chat.id}")
            print(f"🔍 [DEBUG RANKING] Message ID: {call.message.message_id}")
            call.message.text = '/ranking'
            ranking(call.message)
        except Exception as e:
            print(f"❌ [ERRO RANKING] Erro ao abrir ranking: {e}")
            print(f"❌ [ERRO RANKING] Tipo do erro: {type(e).__name__}")
            safe_send_message(call.from_user.id, "❌ Erro ao carregar ranking. Tente novamente.")
    
    if call.data == 'ranking_recargas':
        try:
            print(f"🔍 [DEBUG RANKING RECARGAS] Iniciando ranking_recargas")
            print(f"🔍 [DEBUG RANKING RECARGAS] User ID: {call.from_user.id}")
            print(f"🔍 [DEBUG RANKING RECARGAS] Chat ID: {call.message.chat.id}")
            print(f"🔍 [DEBUG RANKING RECARGAS] Message ID: {call.message.message_id}")
            ranking_recargas(call.message)
        except Exception as e:
            print(f"❌ [ERRO RANKING RECARGAS] {e}")
            safe_send_message(call.from_user.id, "❌ Erro ao carregar ranking. Tente novamente.")
    
    if call.data == 'ranking_gift':
        try:
            print(f"🔍 [DEBUG RANKING GIFT] Iniciando ranking_gift")
            print(f"🔍 [DEBUG RANKING GIFT] User ID: {call.from_user.id}")
            print(f"🔍 [DEBUG RANKING GIFT] Chat ID: {call.message.chat.id}")
            print(f"🔍 [DEBUG RANKING GIFT] Message ID: {call.message.message_id}")
            ranking_gift(call.message)
        except Exception as e:
            print(f"❌ [ERRO RANKING GIFT] {e}")
            safe_send_message(call.from_user.id, "❌ Erro ao carregar ranking. Tente novamente.")
    
    if call.data == 'ranking_servicos':
        try:
            print(f"🔍 [DEBUG RANKING SERVICOS] Iniciando ranking_servicos")
            print(f"🔍 [DEBUG RANKING SERVICOS] User ID: {call.from_user.id}")
            print(f"🔍 [DEBUG RANKING SERVICOS] Chat ID: {call.message.chat.id}")
            print(f"🔍 [DEBUG RANKING SERVICOS] Message ID: {call.message.message_id}")
            ranking_servico(call.message)
        except Exception as e:
            print(f"❌ [ERRO RANKING SERVICOS] {e}")
            safe_send_message(call.from_user.id, "❌ Erro ao carregar ranking. Tente novamente.")
    
    # ==================== CANCELAMENTO (ccl) CORRIGIDO ====================
    if call.data.split()[0] == 'ccl':
        # Declarar global ANTES de usar
        global cancel_data
        
        call_parts = call.data.split()
        print(f"🔍 [DEBUG CANCELAMENTO] Partes: {call_parts}")

        # --- Verificação de Segurança Inicial ---
        if len(call_parts) < 2:
            print(f"❌ [CANCELAMENTO] Callback mal formatado: {call.data}")
            safe_answer_callback(call, "❌ Erro no formato do cancelamento.", show_alert=True)
            return

        # --- Agora sim, podemos definir as variáveis com segurança ---
        atv = call_parts[1]
        val = None
        num = None
        ser = None
        servico_para_regenerar = None
        provedor_usado = None

        print(f"Processando cancelamento para ativação: {atv}")

        # --- Extrair Dados (Formato Inline vs. Cache) ---
        if len(call_parts) == 5:  # Formato: ccl {id} {valor} {numero} {servico}
            val = float(call_parts[2])
            num = call_parts[3]
            ser = call_parts[4]
            print(f"?? [CANCELAMENTO INLINE] ID: {atv} | Valor: {val} | Número: {num} | Serviço: {ser}")
            
            # Tentar identificar o provedor
            provedor_usado = identificar_provedor_ativacao(atv, call.from_user.id)
            if not provedor_usado:
                provedor_usado = "herosms"
                print(f"⚠️ [CANCELAMENTO] Provedor não identificado, usando padrão: {provedor_usado}")
        else:  # Formato padrão: tentar pegar do cache ou banco de dados
            print(f"🔍 [CANCELAMENTO NORMAL] Buscando dados para ID: {atv}")
            dados = cancel_data.get(str(atv), {})
            val = dados.get('valor')
            num = dados.get('numero')
            ser = dados.get('servico')
            provedor_usado = dados.get('provedor', 'herosms')

            # Fallback para o banco de dados se não encontrar no cache
            if not val or not num or not ser or not provedor_usado:
                print(f"⚠️ [FALLBACK] Buscando no banco de dados...")
                try:
                    with open('database/users.json', 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    for user in data["users"]:
                        if int(user["id"]) == int(call.from_user.id):
                            for compra in user.get("compras", []):
                                if str(compra.get("id_ativacao", "")) == str(atv):
                                    val = compra.get("valor")
                                    num = compra.get("numero")
                                    ser = compra.get("servico")
                                    provedor_usado = compra.get("provedor", "herosms")
                                    print(f"✅ [FALLBACK] Dados recuperados - Provedor: {provedor_usado}")
                                    break
                            if val:
                                break
                except Exception as e:
                    print(f"❌ [FALLBACK] Erro: {e}")
                    if not provedor_usado:
                        provedor_usado = "herosms"

        servico_para_regenerar = ser

        # --- Verificação Final dos Dados ---
        if val is None or num is None or ser is None:
            print(f"❌ [CANCELAMENTO] Dados incompletos para ID {atv}. Cache: {list(cancel_data.keys())}")
            safe_answer_callback(call, "❌ Erro: Dados de cancelamento não encontrados!", show_alert=True)
            return

        print(f"✅ [CANCELAMENTO] Dados carregados - Provedor: {provedor_usado}")

        # --- Verificação de Reembolso Duplicado ---
        if api.InfoUser.verificar_reembolso_duplicado(call.from_user.id, atv):
            print(f"⚠️ [CANCELAMENTO] Ativação {atv} já foi reembolsada.")
            safe_answer_callback(call, "⚠️ Este número já foi cancelado/reembolsado!", show_alert=True)
            try:
                texto_novo = f"❌ <b>ATIVAÇÃO CANCELADA</b>\n\n📱 <b>Número:</b> <code>+{num}</code>\n🎟 <b>Serviço:</b> {ser}\n\n💰 <b>Status:</b> Reembolsado"
                markup = InlineKeyboardMarkup([[InlineKeyboardButton('🏠 Menu', callback_data='menu_start')]])
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=texto_novo, parse_mode='HTML', reply_markup=markup)
            except:
                pass
            return

        # --- VERIFICAÇÃO DE COOLDOWN (CORRIGIDA) ---
        print(f"Verificando cancelamento para ID: {atv}, Usuario: {call.from_user.id}")

        if not api.CooldownCancelamento.ativado():
            print(f"✅ Cooldown de cancelamento DESATIVADO - Liberando cancelamento imediatamente")
            cancelamento_bloqueado = False
            segundos_restantes = 0
            tempo_restante_msg = ""
        else:
            tempo_espera = api.CooldownCancelamento.tempo_espera()
            cancelamento_bloqueado = True
            segundos_restantes = tempo_espera
            compra_encontrada = False
            data_compra_formatada = None

            try:
                with open('database/users.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for user in data["users"]:
                    if int(user["id"]) == int(call.from_user.id):
                        for compra in user.get("compras", []):
                            if str(compra.get("id_ativacao", "")) == str(atv):
                                compra_encontrada = True
                                data_compra = compra.get("data", "")
                                data_compra_formatada = data_compra
                                if data_compra:
                                    from datetime import datetime
                                    
                                    timestamp_compra = None
                                    
                                    for formato in ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y as %H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                                        try:
                                            if "as" in data_compra and formato == "%d/%m/%Y %H:%M:%S":
                                                data_limpa = data_compra.replace(" as ", " ")
                                                data_obj = datetime.strptime(data_limpa, formato)
                                            else:
                                                data_obj = datetime.strptime(data_compra, formato)
                                            timestamp_compra = data_obj.timestamp()
                                            print(f"📅 Data parseada com formato {formato}: {data_compra}")
                                            break
                                        except:
                                            continue
                                    
                                    if timestamp_compra:
                                        timestamp_atual = time.time()
                                        tempo_passado = timestamp_atual - timestamp_compra
                                        
                                        if tempo_passado < tempo_espera:
                                            segundos_restantes = int(tempo_espera - tempo_passado)
                                            print(f"⏳ [COOLDOWN] Tempo passado: {int(tempo_passado)}s, Restante: {segundos_restantes}s")
                                        else:
                                            segundos_restantes = 0
                                            cancelamento_bloqueado = False
                                            print(f"✅ [COOLDOWN] Já passou {int(tempo_passado)}s, cooldown liberado")
                                    else:
                                        print(f"⚠️ [COOLDOWN] Não foi possível parsear a data: {data_compra}")
                                break
                        break
            except Exception as e:
                print(f"Erro ao verificar histórico: {e}")
                cancelamento_bloqueado = True
                segundos_restantes = tempo_espera

            # Calcular tempo restante para mensagem amigável
            if cancelamento_bloqueado and segundos_restantes > 0:
                minutos_rest = segundos_restantes // 60
                segs_rest = segundos_restantes % 60
                
                if minutos_rest > 0:
                    tempo_restante_msg = f"{minutos_rest} minuto{'s' if minutos_rest > 1 else ''}"
                    if segs_rest > 0:
                        tempo_restante_msg += f" e {segs_rest} segundo{'s' if segs_rest > 1 else ''}"
                else:
                    tempo_restante_msg = f"{segs_rest} segundo{'s' if segs_rest > 1 else ''}"
            else:
                tempo_restante_msg = ""

            print(f"Resultado: cancelamento_bloqueado = {cancelamento_bloqueado}, segundos_restantes = {segundos_restantes}")

        if cancelamento_bloqueado and segundos_restantes > 0:
            # ⚠️ MOSTRAR MENSAGEM COM O TEMPO CORRETO
            print(f"Cancelamento BLOQUEADO - Tempo restante: {tempo_restante_msg}")
            
            # Mensagem personalizada com o tempo
            mensagem_cooldown = (
                f"⏳ <b>AGUARDE PARA CANCELAR!</b>\n\n"
                f"❌ Você não pode cancelar este número ainda.\n\n"
                f"📅 <b>Data da compra:</b> {data_compra_formatada if data_compra_formatada else 'N/A'}\n"
                f"⏱️ <b>Tempo mínimo de espera:</b> {tempo_espera} segundos\n"
                f"🕐 <b>Tempo restante:</b> <code>{tempo_restante_msg}</code>\n\n"
                f"💡 Após este período, você poderá cancelar e receber o reembolso."
            )
            
            # Editar a mensagem original mostrando o tempo
            try:
                markup_cooldown = InlineKeyboardMarkup([
                    [InlineKeyboardButton('🔙 Voltar', callback_data='menu_start')]
                ])
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=mensagem_cooldown,
                    parse_mode='HTML',
                    reply_markup=markup_cooldown
                )
            except Exception as e:
                print(f"Erro ao editar mensagem de cooldown: {e}")
            
            # Responder o callback para não travar o botão
            try:
                bot.answer_callback_query(call.id, f"⏳ Aguarde {tempo_restante_msg} para cancelar!", show_alert=True)
            except:
                pass
            
            return
        else:
            print(f"✅ Cancelamento LIBERADO")

        print(f"=== LOG CANCELAMENTO MANUAL ===")
        print(f"ID da ativação: {atv}")
        print(f"Usuário: {call.message.chat.first_name} (ID: {call.message.chat.id})")
        print(f"Número: {num}")
        print(f"Serviço: {ser}")
        print(f"Valor a ser estornado: R${float(val):.2f}")
        print(f"Provedor identificado: {provedor_usado}")
        print(f"Tentando cancelar na API...")

        # Tentar cancelar com o provedor identificado
        m = api.InfoApi.mudar_status_numero(atv, '8', provedor_usado)
        print(f"Resposta da API para cancelamento (1ª tentativa - {provedor_usado}): {m}")

        # Se falhou, tentar no outro provedor
        if m != 'ACCESS_CANCEL' and 'BAD_STATUS' in str(m):
            outro_provedor = "grizzly" if provedor_usado == "herosms" else "herosms"
            print(f"⚠️ BAD_STATUS detectado! Tentando no provedor alternativo: {outro_provedor}")
            
            m2 = api.InfoApi.mudar_status_numero(atv, '8', outro_provedor)
            print(f"Resposta da API para cancelamento (2ª tentativa - {outro_provedor}): {m2}")
            
            if m2 == 'ACCESS_CANCEL':
                m = m2
                provedor_usado = outro_provedor
                print(f"✅ Cancelamento bem-sucedido no provedor alternativo: {outro_provedor}")

        # Verificar status atual
        try:
            status_final = api.InfoApi.pegar_status_numero(atv)
            print(f"📊 [STATUS FINAL] ID:{atv} | Status: {repr(status_final)}")
        except Exception as e:
            print(f"⚠️ [ERRO STATUS FINAL] {e}")
            status_final = None

        if status_final == False and m != 'ACCESS_CANCEL':
            print("✅ [NORMALIZADO] Ativação já cancelada - tratando como sucesso e prosseguindo com reembolso")
            m = 'ACCESS_CANCEL'

        if isinstance(m, str) and m == 'INVALID_ID' and status_final == False:
            print("⚠️ [INVALID_ID] Status indica cancelado - normalizando para ACCESS_CANCEL")
            m = 'ACCESS_CANCEL'

        if type(m) == str:
            if m == 'EARLY_CANCEL_DENIED':
                if api.CooldownCancelamento.ativado():
                    safe_answer_callback(call, "Espere 5 minutos para cancelar!", show_alert=True)
                    return
                else:
                    print(f"⚠️ Cancelamento bloqueado pela API (EARLY_CANCEL_DENIED) mas cooldown está DESATIVADO - Forçando como sucesso...")
                    m = 'ACCESS_CANCEL'
            
            if m == 'ACCESS_CANCEL':
                if not api.InfoUser.verificar_reembolso_duplicado(call.message.chat.id, atv):
                    api.InfoUser.marcar_como_reembolsado(call.message.chat.id, atv)
                    api.InfoUser.add_saldo(call.message.chat.id, float(val))

                    try:
                        with open('database/users.json', 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            for user in data["users"]:
                                if int(user["id"]) == int(call.message.chat.id):
                                    for compra in user["compras"]:
                                        if str(compra.get("id_ativacao", "")) == str(atv):
                                            message_id_original = compra.get("message_id")
                                            if message_id_original:
                                                bot.delete_message(chat_id=call.message.chat.id, message_id=message_id_original)
                                            break
                                    break
                    except Exception as e:
                        print(f"Erro ao deletar mensagem original: {e}")

                    safe_answer_callback(call, "✅ Reembolsado com sucesso!", show_alert=True)
                    
                    saldo_atual = api.InfoUser.saldo(call.message.chat.id)
                    texto_cancelamento = (
                        f"☑️ <b>ATIVAÇÃO CANCELADA!</b>\n\n"
                        f"❌ <b>Número removido com sucesso</b>\n"
                        f"💰 <b>Valor reembolsado:</b> R${float(val):.2f}\n"
                        f"💳 <b>Saldo atual:</b> R${saldo_atual:.2f}\n\n"
                        f"🔄 <b>O que deseja fazer agora?</b>"
                    )
                    markup_cancelamento = InlineKeyboardMarkup([
                        [InlineKeyboardButton('🔄 Gerar Novamente', callback_data=f'delmsg_gerar_novamente {servico_para_regenerar}')],
                        [InlineKeyboardButton('🔥 Ver serviços', callback_data='delmsg_servicos')],
                        [InlineKeyboardButton('🏠 Menu', callback_data='delmsg_menu_start')]
                    ])
                    
                    try:
                        bot.send_message(chat_id=call.message.chat.id, text=texto_cancelamento, parse_mode='HTML', reply_markup=markup_cancelamento)
                    except Exception as e:
                        print(f"Erro ao enviar mensagem de cancelamento: {e}")
                else:
                    safe_answer_callback(call, "⚠️ Já foi reembolsado!", show_alert=True)
                    return
            else:
                safe_answer_callback(call, "❌ Erro no cancelamento. Tente novamente.", show_alert=True)
                return
        else:
            safe_answer_callback(call, "❌ Erro no cancelamento. Tente novamente.", show_alert=True)
            return
        
        try:
            destino_log = api.Log.destino_log_cancelousms()
            if destino_log and destino_log not in ["SEUID", "ID"]:
                clients = api.sms_clients_all()
                provedor_index = 1
                for idx, client in enumerate(clients, start=1):
                    if client.provider == provedor_usado:
                        provedor_index = idx
                        break
                
                log_cancel = (
                    f"👤 <b>CANCELAMENTO MANUAL</b>\n\n"
                    f"🙋 <b>USER:</b> {call.message.chat.id}\n"
                    f"💰 <b>VALOR:</b> R${float(val):.2f}\n"
                    f"📱 <b>NUMERO:</b> <code>{num}</code>\n"
                    f"🎟 <b>SERVIÇO:</b> {ser}\n"
                    f"🏢 <b>PROVEDOR:</b> Provedor {provedor_index}\n"
                    f"🔄 <b>MOTIVO:</b> Cancelado pelo usuário"
                )
                bot.send_message(destino_log, log_cancel, parse_mode='HTML')
        except Exception as e:
            print(f"Erro ao enviar log de cancelamento: {e}")
        
        return

threading.Thread(target=alertar_saldo_baixo_api).start()
threading.Thread(target=disparar_alertas).start()

@bot.message_handler(commands=['cooldown'])
def verificar_cooldown(message):
    if not api.Admin.verificar_admin(message.chat.id):
        bot.reply_to(message, "❌ Você não tem permissão para usar este comando!")
        return
    
    try:
        if len(message.text.split()) < 2:
            bot.reply_to(message, "❌ Uso: /cooldown <ID_DO_USUARIO>")
            return
        
        user_id = int(message.text.split()[1])
        
        if not api.InfoUser.verificar_usuario(user_id):
            bot.reply_to(message, f"❌ Usuário {user_id} não encontrado!")
            return
        
        cooldowns = api.sms_cooldown.cooldowns.get(user_id, {})
        
        if not cooldowns:
            bot.reply_to(message, f"✅ Usuário {user_id} não tem cooldowns ativos.")
            return
        
        msg = f"⏰ <b>COOLDOWNS ATIVOS - Usuário {user_id}</b>\n\n"
        
        current_time = time.time()
        for service_id, timestamp in cooldowns.items():
            time_diff = current_time - timestamp
            remaining = api.sms_cooldown.cooldown_duration - time_diff
            
            if remaining > 0:
                minutes = int(remaining) // 60
                seconds = int(remaining) % 60
                time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
                msg += f"• <b>{service_id}</b>: {time_str}\n"
        
        bot.reply_to(message, msg, parse_mode='HTML')
        
    except ValueError:
        bot.reply_to(message, "❌ ID de usuário inválido!")
    except Exception as e:
        bot.reply_to(message, f"❌ Erro: {e}")

@bot.message_handler(commands=['clearcooldown'])
def limpar_cooldown(message):
    if not api.Admin.verificar_admin(message.chat.id):
        bot.reply_to(message, "❌ Você não tem permissão para usar este comando!")
        return
    
    try:
        if len(message.text.split()) < 2:
            bot.reply_to(message, "❌ Uso: /clearcooldown <ID_DO_USUARIO> [SERVIÇO]")
            return
        
        user_id = int(message.text.split()[1])
        
        if not api.InfoUser.verificar_usuario(user_id):
            bot.reply_to(message, f"❌ Usuário {user_id} não encontrado!")
            return
        
        if len(message.text.split()) >= 3:
            service_id = message.text.split()[2]
            if user_id in api.sms_cooldown.cooldowns and service_id in api.sms_cooldown.cooldowns[user_id]:
                del api.sms_cooldown.cooldowns[user_id][service_id]
                bot.reply_to(message, f"✅ Cooldown do serviço {service_id} removido para o usuário {user_id}!")
            else:
                bot.reply_to(message, f"❌ Usuário {user_id} não tem cooldown ativo para o serviço {service_id}!")
        else:
            if user_id in api.sms_cooldown.cooldowns:
                del api.sms_cooldown.cooldowns[user_id]
                bot.reply_to(message, f"✅ Todos os cooldowns do usuário {user_id} foram removidos!")
            else:
                bot.reply_to(message, f"✅ Usuário {user_id} não tem cooldowns ativos.")
        
    except ValueError:
        bot.reply_to(message, "❌ ID de usuário inválido!")
    except Exception as e:
        bot.reply_to(message, f"❌ Erro: {e}")

# Registrar comandos do bot
def set_my_commands():
    try:
        commands = [
            telebot.types.BotCommand("/start", "Iniciar o bot"),
            telebot.types.BotCommand("/pix", "Gerar código PIX"),
            telebot.types.BotCommand("/servicos", "Ver serviços disponíveis"),
            telebot.types.BotCommand("/saldo", "Ver seu saldo"),
            telebot.types.BotCommand("/perfil", "Ver seu perfil"),
            telebot.types.BotCommand("/recarga", "Ver histórico de recargas"),
            telebot.types.BotCommand("/paises", "Escolher país"),
            telebot.types.BotCommand("/ajuda", "Obter ajuda")
        ]
        bot.set_my_commands(commands)
        print(f"✅ Comandos do bot registrados com sucesso!")
    except Exception as e:
        log_print(f"❌ Erro ao registrar comandos: {e}")

# Iniciar webhook em thread separada
def iniciar_webhook():
    try:
        import socket
        try:
            import webhook
        except ImportError:
            log_print("⚠️ Módulo 'webhook' não encontrado. Webhook Zucpay não será iniciado.")
            log_print("💡 Se você precisa do webhook, crie o arquivo 'webhook.py' com a aplicação Flask.")
            return
        
        def verificar_porta(port):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(('0.0.0.0', port))
                sock.close()
                return True
            except OSError:
                return False
        
        porta = 8080
        if not verificar_porta(porta):
            log_print(f"⚠️ Porta {porta} já está em uso. Tentando porta alternativa...")
            porta_encontrada = False
            for porta_alt in [8080, 8081, 8082, 8083, 8084, 8085]:
                if verificar_porta(porta_alt):
                    porta = porta_alt
                    porta_encontrada = True
                    log_print(f"✅ Usando porta alternativa: {porta}")
                    break
            if not porta_encontrada:
                log_print(f"❌ Nenhuma porta disponível encontrada (8080-8085). Webhook não será iniciado.")
                return
        else:
            log_print(f"✅ Porta {porta} disponível. Iniciando webhook...")
        
        webhook.app.run(host='0.0.0.0', port=porta, debug=False)
    except OSError as e:
        if "Address already in use" in str(e) or "address is already in use" in str(e).lower():
            log_print(f"⚠️ Porta {porta} já está em uso. Webhook não será iniciado.")
        else:
            log_print(f"❌ Erro ao iniciar webhook: {e}")
    except Exception as e:
        log_print(f"❌ Erro ao iniciar webhook: {e}")

# Registrar comandos quando o bot inicia
set_my_commands()

# ==================== BROADCAST GROUPS SCHEDULER ====================
broadcast_scheduler = BackgroundScheduler()

def executar_distribuicao_broadcast(broadcast_id):
    try:
        broadcast = api.BroadcastMessage.obter_broadcast(broadcast_id)
        if not broadcast:
            print(f"❌ Broadcast {broadcast_id} não encontrado!")
            return
        
        print(f"📤 Iniciando distribuição automática de '{broadcast['nome']}' para {len(broadcast.get('grupos_destino', []))} grupo(s)...")
        
        grupos_destino = broadcast.get('grupos_destino', [])
        
        if not grupos_destino:
            print(f"⚠️ Broadcast '{broadcast['nome']}' não tem grupos de destino definidos!")
            return
        
        total_sucesso = 0
        total_erro = 0
        
        for grupo_id in grupos_destino:
            try:
                print(f"  📤 Enviando para grupo {grupo_id}...")
                
                if broadcast['imagem_file_id']:
                    bot.send_photo(
                        grupo_id,
                        broadcast['imagem_file_id'],
                        caption=broadcast['mensagem'],
                        parse_mode='HTML'
                    )
                else:
                    bot.send_message(grupo_id, broadcast['mensagem'], parse_mode='HTML')
                
                api.BroadcastDelivery.registrar_entrega(broadcast_id, grupo_id, sucesso=True)
                total_sucesso += 1
                print(f"  ✅ Enviado para grupo {grupo_id}")
            except Exception as e:
                api.BroadcastDelivery.registrar_entrega(broadcast_id, grupo_id, sucesso=False, erro_msg=str(e))
                total_erro += 1
                print(f"  ❌ Erro ao enviar para grupo {grupo_id}: {e}")

        print(f"  ℹ️ Broadcast '{broadcast['nome']}' finalizou rodada. Sucesso acumulado: {total_sucesso}, Erro acumulado: {total_erro}")
        
        api.BroadcastMessage.atualizar_ultimo_envio(broadcast_id)
        
        print(f"✅ Distribuição de '{broadcast['nome']}' finalizada! Sucesso: {total_sucesso}, Erro: {total_erro}")
    except Exception as e:
        print(f"❌ Erro ao distribuir broadcast {broadcast_id}: {e}")

def agendar_grupos_divulgacao():
    broadcasts = api.BroadcastMessage.carregar_broadcasts()
    print(f"🗓️ Agendando broadcasts ativos... total carregado: {len(broadcasts)}")
    
    for broadcast in broadcasts:
        if broadcast['ativo']:
            job_id = f"broadcast_{broadcast['id']}"
            try:
                broadcast_scheduler.remove_job(job_id)
                print(f"♻️ Job antigo removido: {job_id}")
            except:
                pass
            
            try:
                broadcast_scheduler.add_job(
                    func=executar_distribuicao_broadcast,
                    args=[broadcast['id']],
                    trigger=IntervalTrigger(minutes=broadcast['intervalo_minutos']),
                    id=job_id,
                    name=f"Broadcast: {broadcast['nome']}",
                    max_instances=1
                )
                print(f"✅ Broadcast '{broadcast['nome']}' agendado para cada {broadcast['intervalo_minutos']} minuto(s)")
            except Exception as e:
                print(f"❌ Erro ao agendar broadcast '{broadcast['nome']}': {e}")
        else:
            print(f"⏸️ Broadcast '{broadcast['nome']}' está inativo, não será agendado")

def disparar_primeira_execucao_broadcasts():
    try:
        broadcasts = api.BroadcastMessage.carregar_broadcasts()
        ativos = [b for b in broadcasts if b.get('ativo')]
        print(f"🚀 Disparando primeira execução imediata de {len(ativos)} broadcast(s) ativo(s)...")
        for b in ativos:
            threading.Thread(target=executar_distribuicao_broadcast, args=(b['id'],), daemon=True).start()
    except Exception as e:
        print(f"❌ Erro ao disparar primeira execução: {e}")

def iniciar_scheduler_broadcast():
    try:
        if not broadcast_scheduler.running:
            broadcast_scheduler.start()
            agendar_grupos_divulgacao()
            disparar_primeira_execucao_broadcasts()
            print("✅ Scheduler de divulgação iniciado")
        else:
            print("ℹ️ Scheduler de divulgação já estava em execução; revalidando agendas...")
            agendar_grupos_divulgacao()
            disparar_primeira_execucao_broadcasts()
    except Exception as e:
        print(f"❌ Erro ao iniciar scheduler de divulgação: {e}")

threading.Thread(target=iniciar_scheduler_broadcast, daemon=True).start()

# ==================== RELATÓRIO MENSAL AUTOMÁTICO ====================
relatorio_scheduler = BackgroundScheduler()

def gerar_relatorio_mensal():
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import io
        
        print("📊 [RELATÓRIO MENSAL] Gerando relatório...")
        
        hoje = datetime.datetime.now()
        if hoje.month == 1:
            mes_anterior = 12
            ano_anterior = hoje.year - 1
        else:
            mes_anterior = hoje.month - 1
            ano_anterior = hoje.year
        
        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        nome_mes = meses[mes_anterior]
        
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        
        total_recargas = 0
        valor_recargas = 0
        total_compras = 0
        valor_compras = 0
        novos_usuarios = 0
        
        for user in data["users"]:
            for recarga in user.get("pagamentos", []):
                try:
                    data_recarga = recarga["data"].split(' ')[0]
                    dia, mes, ano = data_recarga.split('/')
                    if int(mes) == mes_anterior and int(ano) == ano_anterior:
                        total_recargas += 1
                        valor_recargas += float(recarga["valor"])
                except:
                    continue
            
            for compra in user.get("compras", []):
                try:
                    data_compra = compra["data"].split(' ')[0]
                    dia, mes, ano = data_compra.split('/')
                    if int(mes) == mes_anterior and int(ano) == ano_anterior:
                        total_compras += 1
                        valor_compras += float(compra["valor"])
                except:
                    continue
            
            try:
                data_registro = user.get("data_registro", "")
                if data_registro:
                    data_obj = datetime.datetime.fromisoformat(data_registro)
                    if data_obj.month == mes_anterior and data_obj.year == ano_anterior:
                        novos_usuarios += 1
            except Exception as e:
                try:
                    if '/' in data_registro:
                        dia, mes, ano = data_registro.split('/')
                        if int(mes) == mes_anterior and int(ano) == ano_anterior:
                            novos_usuarios += 1
                except:
                    pass
        
        lucro = valor_recargas - valor_compras
        
        ticket_medio_recarga = valor_recargas / total_recargas if total_recargas > 0 else 0
        ticket_medio_compra = valor_compras / total_compras if total_compras > 0 else 0
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'Relatório Mensal - {nome_mes}/{ano_anterior}', fontsize=16, fontweight='bold')
        
        categorias = ['Recargas', 'Compras']
        valores = [valor_recargas, valor_compras]
        cores = ['#4CAF50', '#F44336']
        ax1.bar(categorias, valores, color=cores, alpha=0.7, edgecolor='black')
        ax1.set_title('Recargas vs Compras (R$)', fontweight='bold')
        ax1.set_ylabel('Valor (R$)')
        for i, v in enumerate(valores):
            ax1.text(i, v + max(valores)*0.02, f'R${v:.2f}', ha='center', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        lucro_cor = '#4CAF50' if lucro >= 0 else '#F44336'
        ax2.bar(['Lucro'], [lucro], color=lucro_cor, alpha=0.7, edgecolor='black')
        ax2.set_title('Lucro Bruto', fontweight='bold')
        ax2.set_ylabel('Valor (R$)')
        ax2.text(0, lucro + abs(lucro)*0.05 if lucro >= 0 else lucro - abs(lucro)*0.05, 
                 f'R${lucro:.2f}', ha='center', fontweight='bold')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.grid(axis='y', alpha=0.3)
        
        categorias_qtd = ['Recargas', 'Compras']
        quantidades = [total_recargas, total_compras]
        cores_qtd = ['#2196F3', '#FF9800']
        ax3.bar(categorias_qtd, quantidades, color=cores_qtd, alpha=0.7, edgecolor='black')
        ax3.set_title('Quantidade de Transações', fontweight='bold')
        ax3.set_ylabel('Quantidade')
        for i, v in enumerate(quantidades):
            ax3.text(i, v + max(quantidades)*0.02, str(v), ha='center', fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        categorias_users = ['Novos\nUsuários', 'Total\nUsuários']
        usuarios_valores = [novos_usuarios, len(data['users'])]
        cores_users = ['#9C27B0', '#3F51B5']
        ax4.bar(categorias_users, usuarios_valores, color=cores_users, alpha=0.7, edgecolor='black')
        ax4.set_title('Usuários', fontweight='bold')
        ax4.set_ylabel('Quantidade')
        for i, v in enumerate(usuarios_valores):
            ax4.text(i, v + max(usuarios_valores)*0.02, str(v), ha='center', fontweight='bold')
        ax4.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        texto = f"📊 <b>RELATÓRIO MENSAL - {nome_mes.upper()}/{ano_anterior}</b>\n\n"
        texto += f"━━━━━━━━━━━━━━━━━━━━\n\n"
        
        texto += f"💰 <b>RECARGAS</b>\n"
        texto += f"   • Total: {total_recargas} recargas\n"
        texto += f"   • Valor: R${valor_recargas:.2f}\n"
        texto += f"   • Ticket médio: R${ticket_medio_recarga:.2f}\n\n"
        
        texto += f"🛒 <b>COMPRAS (SMS)</b>\n"
        texto += f"   • Total: {total_compras} compras\n"
        texto += f"   • Valor: R${valor_compras:.2f}\n"
        texto += f"   • Ticket médio: R${ticket_medio_compra:.2f}\n\n"
        
        texto += f"📈 <b>LUCRO</b>\n"
        texto += f"   • Lucro bruto: R${lucro:.2f}\n"
        if valor_recargas > 0:
            margem = (lucro / valor_recargas) * 100
            texto += f"   • Margem: {margem:.1f}%\n\n"
        else:
            texto += f"   • Margem: 0%\n\n"
        
        texto += f"👥 <b>USUÁRIOS</b>\n"
        texto += f"   • Novos usuários: {novos_usuarios}\n"
        texto += f"   • Total de usuários: {len(data['users'])}\n\n"
        
        texto += f"━━━━━━━━━━━━━━━━━━━━\n"
        texto += f"📅 <b>Relatório gerado em:</b> {hoje.strftime('%d/%m/%Y às %H:%M')}"
        
        admin_id = api.CredentialsChange.id_dono()
        bot.send_photo(admin_id, buf, caption=texto, parse_mode='HTML')
        print(f"✅ [RELATÓRIO MENSAL] Relatório de {nome_mes}/{ano_anterior} enviado para admin {admin_id}")
        
    except Exception as e:
        print(f"❌ [RELATÓRIO MENSAL] Erro ao gerar relatório: {e}")
        import traceback
        print(traceback.format_exc())

def iniciar_scheduler_relatorio_mensal():
    try:
        if not relatorio_scheduler.running:
            relatorio_scheduler.start()
            print("✅ [RELATÓRIO MENSAL] Scheduler iniciado")
        
        try:
            relatorio_scheduler.remove_job('relatorio_mensal')
        except:
            pass
        
        relatorio_scheduler.add_job(
            func=gerar_relatorio_mensal,
            trigger='cron',
            day=1,
            hour=9,
            minute=0,
            id='relatorio_mensal',
            replace_existing=True
        )
        
        print("📅 [RELATÓRIO MENSAL] Agendado para todo dia 1 às 09:00")
        
    except Exception as e:
        print(f"❌ [RELATÓRIO MENSAL] Erro ao iniciar scheduler: {e}")

threading.Thread(target=iniciar_scheduler_relatorio_mensal, daemon=True).start()

# ==================== SISTEMA DE AUDITORIA ====================
def obter_info_usuario_telegram(user_id):
    try:
        chat = bot.get_chat(user_id)
        nome = chat.first_name or ""
        if chat.last_name:
            nome += f" {chat.last_name}"
        username = f"@{chat.username}" if chat.username else "Sem username"
        return nome.strip() or "N/A", username
    except Exception as e:
        return "N/A", "N/A"

def verificar_inconsistencias():
    try:
        print("🔍 [AUDITORIA] Iniciando verificação de inconsistências...")
        
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        
        inconsistencias = []
        usuarios_suspeitos = []
        
        cache_usuarios = {}
        
        for user in data["users"]:
            user_id = user.get("id")
            saldo = float(user.get("saldo", 0))
            compras = user.get("compras", [])
            pagamentos = user.get("pagamentos", [])
            
            if user_id not in cache_usuarios:
                nome, username = obter_info_usuario_telegram(user_id)
                cache_usuarios[user_id] = {"nome": nome, "username": username}
            
            user_info = cache_usuarios[user_id]
            
            total_gasto = 0
            for compra in compras:
                status_compra = compra.get("status", "ativa")
                if status_compra == "concluida":
                    total_gasto += float(compra.get("valor", 0))
            
            total_recargas = 0
            for pagamento in pagamentos:
                status = pagamento.get("status", "approved")
                if status == "approved" or status not in ["pending", "cancelled", "failed"]:
                    total_recargas += float(pagamento.get("valor", 0))
            
            saldo_esperado = total_recargas - total_gasto
            diferenca = abs(saldo - saldo_esperado)
            
            if diferenca > 0.10:
                inconsistencias.append({
                    "tipo": "SALDO_INCOMPATÍVEL",
                    "user_id": user_id,
                    "nome": user_info["nome"],
                    "username": user_info["username"],
                    "saldo_atual": saldo,
                    "saldo_esperado": saldo_esperado,
                    "diferenca": diferenca,
                    "total_recargas": total_recargas,
                    "total_gasto": total_gasto,
                    "total_compras": len(compras)
                })
            
            if saldo < -0.01:
                inconsistencias.append({
                    "tipo": "SALDO_NEGATIVO",
                    "user_id": user_id,
                    "nome": user_info["nome"],
                    "username": user_info["username"],
                    "saldo": saldo
                })
            
            ids_pagamentos = [p.get("id_pagamento") for p in pagamentos if p.get("id_pagamento")]
            if len(ids_pagamentos) != len(set(ids_pagamentos)):
                duplicados = [id_pag for id_pag in ids_pagamentos if ids_pagamentos.count(id_pag) > 1]
                inconsistencias.append({
                    "tipo": "PAGAMENTOS_DUPLICADOS",
                    "user_id": user_id,
                    "nome": user_info["nome"],
                    "username": user_info["username"],
                    "ids_duplicados": list(set(duplicados)),
                    "total_pagamentos": len(pagamentos)
                })
            
            if len(compras) > 5 and total_recargas == 0:
                usuarios_suspeitos.append({
                    "tipo": "COMPRAS_SEM_RECARGA",
                    "user_id": user_id,
                    "nome": user_info["nome"],
                    "username": user_info["username"],
                    "total_compras": len(compras),
                    "total_gasto": total_gasto,
                    "saldo_atual": saldo
                })
            
            if saldo > 50 and total_recargas < saldo * 0.5:
                usuarios_suspeitos.append({
                    "tipo": "SALDO_ALTO_SEM_RECARGA",
                    "user_id": user_id,
                    "nome": user_info["nome"],
                    "username": user_info["username"],
                    "saldo": saldo,
                    "total_recargas": total_recargas
                })
            
            for compra in compras:
                valor_compra = float(compra.get("valor", 0))
                if valor_compra <= 0:
                    inconsistencias.append({
                        "tipo": "COMPRA_VALOR_INVALIDO",
                        "user_id": user_id,
                        "nome": user_info["nome"],
                        "username": user_info["username"],
                        "id_ativacao": compra.get("id_ativacao"),
                        "valor": valor_compra,
                        "servico": compra.get("servico")
                    })
        
        total_inconsistencias = len(inconsistencias) + len(usuarios_suspeitos)
        
        if total_inconsistencias > 0:
            print(f"⚠️ [AUDITORIA] {total_inconsistencias} inconsistência(s) encontrada(s)")
            
            cabecalho = (
                f"🔍 <b>RELATÓRIO DE AUDITORIA</b>\n\n"
                f"📅 <b>Data:</b> {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"📊 <b>Total de inconsistências:</b> {total_inconsistencias}\n\n"
            )
            
            mensagens = []
            
            if inconsistencias:
                msg_atual = cabecalho + f"🚨 <b>INCONSISTÊNCIAS CRÍTICAS ({len(inconsistencias)}):</b>\n\n"
                contador = 0
                
                for inc in inconsistencias:
                    contador += 1
                    tipo = inc["tipo"]
                    user_id = inc["user_id"]
                    nome = inc.get("nome", "N/A")
                    username = inc.get("username", "N/A")
                    
                    item_texto = ""
                    if tipo == "SALDO_INCOMPATÍVEL":
                        item_texto = (
                            f"{contador}. 💰 <b>Saldo Incompatível</b>\n"
                            f"   👤 ID: <code>{user_id}</code>\n"
                            f"   📝 Nome: {nome}\n"
                            f"   🔗 Username: {username}\n"
                            f"   💰 Saldo atual: R${inc['saldo_atual']:.2f}\n"
                            f"   📊 Saldo esperado: R${inc['saldo_esperado']:.2f}\n"
                            f"   ⚠️ Diferença: R${inc['diferenca']:.2f}\n"
                            f"   📥 Recargas: R${inc['total_recargas']:.2f}\n"
                            f"   📤 Gastos: R${inc['total_gasto']:.2f}\n\n"
                        )
                    
                    elif tipo == "SALDO_NEGATIVO":
                        item_texto = (
                            f"{contador}. ❌ <b>Saldo Negativo</b>\n"
                            f"   👤 ID: <code>{user_id}</code>\n"
                            f"   📝 Nome: {nome}\n"
                            f"   🔗 Username: {username}\n"
                            f"   💵 Saldo: R${inc['saldo']:.2f}\n\n"
                        )
                    
                    elif tipo == "PAGAMENTOS_DUPLICADOS":
                        item_texto = (
                            f"{contador}. 🔄 <b>Pagamentos Duplicados</b>\n"
                            f"   👤 ID: <code>{user_id}</code>\n"
                            f"   📝 Nome: {nome}\n"
                            f"   🔗 Username: {username}\n"
                            f"   📋 IDs duplicados: {len(inc['ids_duplicados'])}\n"
                            f"   📊 Total pagamentos: {inc['total_pagamentos']}\n\n"
                        )
                    
                    elif tipo == "COMPRA_VALOR_INVALIDO":
                        item_texto = (
                            f"{contador}. ⚠️ <b>Compra com Valor Inválido</b>\n"
                            f"   👤 ID: <code>{user_id}</code>\n"
                            f"   📝 Nome: {nome}\n"
                            f"   🔗 Username: {username}\n"
                            f"   🆔 Ativação: {inc['id_ativacao']}\n"
                            f"   💵 Valor: R${inc['valor']:.2f}\n"
                            f"   📱 Serviço: {inc['servico']}\n\n"
                        )
                    
                    if len(msg_atual + item_texto) > 3800:
                        msg_atual += f"\n<i>(Continua na próxima mensagem...)</i>"
                        mensagens.append(msg_atual)
                        msg_atual = f"🔍 <b>RELATÓRIO DE AUDITORIA (Continuação)</b>\n\n"
                    
                    msg_atual += item_texto
                
                if msg_atual and msg_atual != f"🔍 <b>RELATÓRIO DE AUDITORIA (Continuação)</b>\n\n":
                    mensagens.append(msg_atual)
            
            if usuarios_suspeitos:
                suspeitos_texto = f"🔎 <b>USUÁRIOS SUSPEITOS ({len(usuarios_suspeitos)}):</b>\n\n"
                contador_sus = 0
                
                for sus in usuarios_suspeitos:
                    contador_sus += 1
                    tipo = sus["tipo"]
                    user_id = sus["user_id"]
                    nome = sus.get("nome", "N/A")
                    username = sus.get("username", "N/A")
                    
                    item_texto = ""
                    if tipo == "COMPRAS_SEM_RECARGA":
                        item_texto = (
                            f"{contador_sus}. 🛒 <b>Muitas Compras Sem Recarga</b>\n"
                            f"   👤 ID: <code>{user_id}</code>\n"
                            f"   📝 Nome: {nome}\n"
                            f"   🔗 Username: {username}\n"
                            f"   🛍️ Compras: {sus['total_compras']}\n"
                            f"   💸 Gasto total: R${sus['total_gasto']:.2f}\n"
                            f"   💰 Saldo atual: R${sus['saldo_atual']:.2f}\n\n"
                        )
                    
                    elif tipo == "SALDO_ALTO_SEM_RECARGA":
                        item_texto = (
                            f"{contador_sus}. 💎 <b>Saldo Alto Sem Recarga Proporcional</b>\n"
                            f"   👤 ID: <code>{user_id}</code>\n"
                            f"   📝 Nome: {nome}\n"
                            f"   🔗 Username: {username}\n"
                            f"   💰 Saldo: R${sus['saldo']:.2f}\n"
                            f"   📥 Recargas: R${sus['total_recargas']:.2f}\n\n"
                        )
                    
                    suspeitos_texto += item_texto
                
                if mensagens and len(mensagens[-1] + suspeitos_texto) < 3800:
                    mensagens[-1] += "\n" + suspeitos_texto
                else:
                    if not mensagens:
                        mensagens.append(cabecalho + suspeitos_texto)
                    else:
                        mensagens.append(f"🔍 <b>RELATÓRIO DE AUDITORIA (Continuação)</b>\n\n" + suspeitos_texto)
            
            if mensagens:
                mensagens[-1] += f"\n⚠️ <b>Ação recomendada:</b> Investigar e corrigir as inconsistências encontradas."
            
            try:
                total_sucessos = 0
                total_falhas = 0
                
                for idx, mensagem in enumerate(mensagens, 1):
                    print(f"📤 [AUDITORIA] Enviando mensagem {idx}/{len(mensagens)}...")
                    
                    sucessos, falhas = enviar_log_multiplos_destinos(mensagem, 'log-auditoria', parse_mode='HTML')
                    total_sucessos += sucessos
                    total_falhas += falhas
                    
                    if idx < len(mensagens):
                        time.sleep(0.5)
                
                if total_sucessos > 0:
                    print(f"✅ [AUDITORIA] {len(mensagens)} mensagem(ns) enviada(s) para {total_sucessos} canal(is) de auditoria")
                else:
                    print(f"⚠️ [AUDITORIA] Nenhum canal configurado, enviando para admin...")
                    dono_id = api.CredentialsChange.id_dono()
                    
                    for idx, mensagem in enumerate(mensagens, 1):
                        bot.send_message(dono_id, mensagem, parse_mode='HTML')
                        if idx < len(mensagens):
                            time.sleep(0.5)
                    
                    print(f"✅ [AUDITORIA] {len(mensagens)} mensagem(ns) enviada(s) para admin (ID: {dono_id})")
                    
            except Exception as e:
                print(f"❌ [AUDITORIA] Erro ao enviar relatório: {e}")
                try:
                    dono_id = api.CredentialsChange.id_dono()
                    
                    for idx, mensagem in enumerate(mensagens, 1):
                        try:
                            bot.send_message(dono_id, f"⚠️ Erro ao enviar relatório de auditoria para canal.\n\n{mensagem[:3900]}", parse_mode='HTML')
                            if idx < len(mensagens):
                                time.sleep(0.5)
                        except Exception as e_msg:
                            print(f"❌ [AUDITORIA] Erro ao enviar mensagem {idx} para admin: {e_msg}")
                            
                except Exception as e2:
                    print(f"❌ [AUDITORIA] Erro ao enviar para admin também: {e2}")
        else:
            print(f"✅ [AUDITORIA] Nenhuma inconsistência encontrada")
        
    except Exception as e:
        import traceback
        print(f"❌ [AUDITORIA] Erro ao verificar inconsistências: {e}")
        print(f"❌ [AUDITORIA] Traceback:\n{traceback.format_exc()}")

# Iniciar webhook em thread separada
threading.Thread(target=iniciar_webhook, daemon=True).start()

bot.infinity_polling()