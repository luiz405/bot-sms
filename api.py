import base64
import gerar_cobranca
import json
import telebot
import requests
import time
import datetime
import random
import threading
import os
import shutil
from datetime import timezone, datetime, timedelta
from pytz import timezone
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from gerencianet import Gerencianet
from credenciais import CREDENTIALS
import logging
import random

def gerar_cpf_valido():
    """Gera um CPF aleatório mas válido"""
    def calcular_digito(cpf_parcial):
        soma = 0
        peso = len(cpf_parcial) + 1
        for i in range(len(cpf_parcial)):
            soma += int(cpf_parcial[i]) * (peso - i)
        digito = 11 - (soma % 11)
        return str(digito) if digito < 10 else '0'
    
    cpf_base = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    cpf_base += calcular_digito(cpf_base)
    cpf_base += calcular_digito(cpf_base)
    
    return cpf_base

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

gn = Gerencianet(CREDENTIALS)

_users_json_lock = threading.Lock()

# ==================== UTILITÁRIOS DE ARQUIVO (SEGUROS) ====================
def _save_users_json_safe(data):
    """Salva users.json de forma SEGURA usando atomic write + backup automático"""
    import os
    import shutil
    from datetime import datetime
    
    try:
        if os.path.exists('database/users.json'):
            backup_name = f'database/users.json.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            shutil.copy2('database/users.json', backup_name)
            print(f"💾 [BACKUP] Backup criado: {backup_name}")
    except Exception as e:
        print(f"⚠️ [BACKUP] Erro ao criar backup: {e}")
    
    temp_file = 'database/users.json.tmp'
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        if os.name == 'nt':
            if os.path.exists('database/users.json'):
                os.remove('database/users.json')
        os.rename(temp_file, 'database/users.json')
        
        print(f"✅ [SAVE] users.json salvo com sucesso")
        return True
    except Exception as e:
        print(f"❌ [SAVE] Erro ao salvar users.json: {e}")
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return False

def _load_users_json_safe():
    """Carrega users.json de forma segura, SEMPRE retorna um dict válido"""
    try:
        if not os.path.exists('database/users.json'):
            print(f"⚠️ [ARQUIVO NAO ENCONTRADO] users.json não encontrado, inicializando estrutura vazia")
            return {"users": []}
        
        with open('database/users.json', 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                print(f"⚠️ [ARQUIVO VAZIO] users.json está vazio, inicializando estrutura")
                return {"users": []}
            
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"❌ [JSON CORROMPIDO] Erro ao ler users.json: {e}")
                return {"users": []}
    except Exception as e:
        print(f"❌ [ERRO INESPERADO] ao carregar users.json: {e}")
        return {"users": []}

# ==================== CLASSE DO PROVEDOR SMS (CORRIGIDA) ====================
class SmsProviderClient:
    HERO_SMS_BASE_URL = "https://hero-sms.com/stubs/handler_api.php"
    GRIZZLY_BASE_URL = "https://api.grizzlysms.com/stubs/handler_api.php"

    def __init__(self, provider: str, api_key: str, timeout: int = 30):
        self.provider = (provider or "herosms").strip().lower()
        self.api_key = (api_key or "").strip()
        self.timeout = timeout
        
        self.session = requests.Session()
        self.session.headers.update({
            'Connection': 'keep-alive',
            'Keep-Alive': 'timeout=30, max=100',
            'User-Agent': 'SMS-Bot/1.0'
        })

    @property
    def base_url(self) -> str:
        if self.provider == "grizzly":
            return self.GRIZZLY_BASE_URL
        return self.HERO_SMS_BASE_URL

    def close(self):
        if hasattr(self, 'session'):
            self.session.close()

    def _request(self, action: str, **params):
        if not self.api_key:
            return {"error": "NO_API_KEY"}

        payload = {"api_key": self.api_key, "action": action}
        for k, v in params.items():
            if v is None:
                continue
            payload[k] = v

        try:
            resp = self.session.get(self.base_url, params=payload, timeout=self.timeout)
            text = (resp.text or "").strip()
        except Exception as e:
            print(f"❌ [API REQUEST ERROR] {action}: {str(e)}")
            return {"error": "REQUEST_FAILED", "details": str(e)}

        if text.startswith("{") or text.startswith("["):
            try:
                return resp.json()
            except Exception:
                return {"error": "BAD_JSON", "raw": text}

        return text

    def getBalance(self):
        r = self._request("getBalance")
        if isinstance(r, str):
            if r.startswith("ACCESS_BALANCE:"):
                try:
                    bal = float(r.split(":", 1)[1])
                except Exception:
                    bal = 0.0
                return {"balance": bal, "raw": r}
            return {"balance": 0.0, "error": r, "raw": r}
        elif isinstance(r, dict):
            if "balance" in r:
                return r
            elif "error" in r:
                return {"balance": 0.0, "error": r.get("error"), "raw": r}
            else:
                return {"balance": 0.0, "raw": r}
        return {"balance": 0.0, "raw": r}

    def getPrices(self, service: str, country: str):
        r = self._request("getPrices", service=service, country=country)
        if isinstance(r, str):
            return {"error": r}
        return r

    def getNumberV2(self, service: str, country: str, operator: str | None = None, maxPrice: str | None = None, fixedPrice: str | None = None):
        params = {"service": service, "country": country}
        if operator is not None:
            params["operator"] = operator
        if maxPrice is not None:
            params["maxPrice"] = maxPrice
        if fixedPrice is not None:
            params["fixedPrice"] = fixedPrice
        
        print(f"[LOG COMPRA] Provedor: {self.provider} | API_KEY: {self.api_key[:5]}...{self.api_key[-5:] if len(self.api_key) > 10 else ''}")
        
        r = self._request("getNumberV2", **params)
        
        # Tratar respostas de erro como strings
        if isinstance(r, str):
            if r.startswith("ACCESS_NUMBER:"):
                try:
                    _, act_id, phone = r.split(":", 2)
                    return {"activationId": int(act_id), "phoneNumber": str(phone), "activationOperator": None, "raw": r}
                except Exception:
                    return {"error": "INVALID_RESPONSE", "raw": r}
            elif r in ["NO_NUMBERS", "NO_BALANCE", "BAD_KEY", "ERROR"]:
                return {"error": r}
            else:
                return {"error": "UNKNOWN_ERROR", "raw": r}
        
        # Se for dict, pode ser sucesso ou erro
        if isinstance(r, dict):
            if "activationId" in r and "phoneNumber" in r:
                return r
            elif "error" in r:
                return r
            else:
                return {"error": "UNKNOWN_RESPONSE", "response": r}
        
        return {"error": "INVALID_RESPONSE", "raw": r}

    def getStatus(self, id: str | int):
        """Obtém status de uma ativação"""
        r = self._request("getStatus", id=id)
        
        # Respostas comuns:
        # STATUS_CANCEL - Cancelado
        # STATUS_WAIT_CODE - Aguardando código
        # STATUS_OK:123456 - Código recebido
        # STATUS_WAIT_RETRY - Aguardando reenvio
        
        if isinstance(r, str):
            return r
        elif isinstance(r, dict):
            if "error" in r:
                return f"ERROR:{r['error']}"
            return str(r)
        return "UNKNOWN_RESPONSE"

    def setStatus(self, id: str | int, status: str | int):
        """Altera status de uma ativação"""
        result = self._request("setStatus", id=id, status=status)

        if isinstance(result, str):
            # Respostas comuns: ACCESS_CANCEL, EARLY_CANCEL_DENIED, etc
            return result
        elif isinstance(result, dict):
            if "error" in result:
                return result["error"]
            return "UNKNOWN_RESPONSE"
        
        return "UNKNOWN_RESPONSE"

    def getTopCountriesByServiceRank(self, service: str, country: str = "", freePrice: bool = True):
        params = {
            "action": "getTopCountriesByServiceRank",
            "service": service,
        }
        if country:
            params["country"] = country
        if freePrice:
            params["freePrice"] = "true"
        return self._request(**params)

    def getRentServicesAndCountries(self, country: str):
        r = self._request("getRentServicesAndCountries", country=country)
        if isinstance(r, str):
            return {"error": r}
        return r

# ==================== FUNÇÕES DE GERENCIAMENTO DE CREDENCIAIS SMS ====================
def _load_credenciais():
    with open('settings/credenciais.json', 'r') as f:
        return json.load(f)

def _save_credenciais(data: dict):
    with open('settings/credenciais.json', 'w') as f:
        json.dump(data, f, indent=4)

def _ensure_sms_provider_migration():
    data = _load_credenciais()
    changed = False

    if "sms_provider" not in data:
        data["sms_provider"] = "herosms"
        changed = True

    if "api-sms-herosms" not in data:
        data["api-sms-herosms"] = ""
        changed = True

    if "api-sms-grizzly" not in data:
        data["api-sms-grizzly"] = ""
        changed = True

    if changed:
        _save_credenciais(data)

    return data

def sms_client() -> SmsProviderClient:
    data = _ensure_sms_provider_migration()
    provider = str(data.get("sms_provider", "herosms")).strip().lower()
    if provider == "grizzly":
        key = str(data.get("api-sms-grizzly", "")).strip()
    else:
        key = str(data.get("api-sms-herosms", "")).strip()
    return SmsProviderClient(provider=provider, api_key=key)

def sms_clients_all():
    """Retorna uma lista de clientes SMS válidos (com API key configurada)"""
    data = _ensure_sms_provider_migration()
    clients = []

    hero_key = str(data.get("api-sms-herosms", "")).strip()
    if hero_key:
        clients.append(SmsProviderClient(provider="herosms", api_key=hero_key))

    grizzly_key = str(data.get("api-sms-grizzly", "")).strip()
    if grizzly_key:
        clients.append(SmsProviderClient(provider="grizzly", api_key=grizzly_key))

    return clients

def get_current_provider_name(provedor_forcado=None):
    """Retorna o nome do provedor atual em formato amigável"""
    try:
        if provedor_forcado:
            if provedor_forcado == "herosms":
                return "Hero-SMS"
            elif provedor_forcado == "grizzly":
                return "GrizzlySMS"
            else:
                return f"Forçado ({provedor_forcado})"

        data = _ensure_sms_provider_migration()
        provider_config = str(data.get("sms_provider", "herosms")).strip().lower()

        if provider_config == "todos":
            clients = sms_clients_all()
            if clients:
                provider = clients[0].provider
                return "Hero-SMS" if provider == "herosms" else "GrizzlySMS"
            return "Todos (Nenhum disponível)"
        elif provider_config == "herosms":
            return "Hero-SMS"
        elif provider_config == "grizzly":
            return "GrizzlySMS"
        else:
            return f"Desconhecido ({provider_config})"
    except Exception as e:
        return f"Erro: {str(e)}"

class SmsProviderProxy:
    def __getattr__(self, item):
        client = sms_client()
        return getattr(client, item)

sms = SmsProviderProxy()

class ApiZucpayInfo:
    def __init__(self):
        try:
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            self.api_key = data.get("zucpay_api_key", "").strip()
            self.base_url = "https://zucpay.com/api/v1"
            self.cpfs = []
            self.carregar_ou_gerar_dados()
            print(f"✅ [ZUCPAY] Configurado com sucesso - API Key: {self.api_key[:20]}...")
        except Exception as e:
            print(f"❌ [ZUCPAY] Erro ao carregar token: {e}")
            self.api_key = ""
            self.cpfs = [self.gerar_cpf_valido() for _ in range(10)]

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def gerar_cpf_valido(self):
        import random
        def calcular_digito(cpf_parcial):
            soma = 0
            peso = len(cpf_parcial) + 1
            for i in range(len(cpf_parcial)):
                soma += int(cpf_parcial[i]) * (peso - i)
            digito = 11 - (soma % 11)
            return str(digito) if digito < 10 else '0'
        cpf_base = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        cpf_base += calcular_digito(cpf_base)
        cpf_base += calcular_digito(cpf_base)
        return cpf_base

    def carregar_ou_gerar_dados(self):
        try:
            with open('settings/cpfs_rotativos.json', 'r') as f:
                data = json.load(f)
            self.cpfs = data.get('cpfs', [])
            if not self.cpfs:
                self.cpfs = [self.gerar_cpf_valido() for _ in range(20)]
            print(f"✅ [ZUCPAY] Carregados {len(self.cpfs)} CPFs do arquivo")
        except FileNotFoundError:
            print("⚠️ [ZUCPAY] Arquivo não encontrado, gerando CPFs aleatórios")
            self.cpfs = [self.gerar_cpf_valido() for _ in range(20)]
        except Exception as e:
            print(f"⚠️ [ZUCPAY] Erro ao carregar CPFs: {e}")
            self.cpfs = [self.gerar_cpf_valido() for _ in range(20)]

    def get_dados_cliente(self):
        import random
        cpf = random.choice(self.cpfs)
        return {"cpf": cpf}

    def criar_pagamento_pix(self, valor, id_usuario):
        try:
            print(f"🚀 [ZUCPAY] Iniciando criação de PIX - Valor: R${valor}")
            dados_cliente = self.get_dados_cliente()
            nome_usuario = f"Cliente {id_usuario}"
            payload = {
                "amount": float(valor),
                "payer": {
                    "name": nome_usuario,
                    "document_value": dados_cliente["cpf"]
                },
                "callback_url": "https://seusite.com/webhook/zucpay"
            }
            headers = self.get_headers()
            print(f"📤 [ZUCPAY] URL: {self.base_url}/pix/deposit")
            response = requests.post(
                f"{self.base_url}/pix/deposit",
                headers=headers,
                json=payload,
                timeout=30
            )
            print(f"📥 [ZUCPAY] Resposta status: {response.status_code}")
            print(f"📥 [ZUCPAY] Resposta texto: {response.text[:500]}")
            if response.status_code in [200, 201, 202]:
                result = response.json()
                if result.get("success") and result.get("data"):
                    data = result["data"]
                    return {
                        "id": data.get("transaction_id") or data.get("id"),
                        "payment_id": data.get("transaction_id") or data.get("id"),
                        "status": data.get("status", "pending"),
                        "qr_code": data.get("qr_code") or data.get("qrCode"),
                        "qr_code_base64": data.get("qr_code_base64") or data.get("qrCodeBase64"),
                        "copyPaste": data.get("copyPaste") or data.get("qr_code"),
                        "value": valor,
                        "provider": "zucpay",
                        "gateway": data.get("gateway")
                    }
                else:
                    print(f"❌ [ZUCPAY] Erro na resposta: {result}")
                    return None
            else:
                print(f"❌ [ZUCPAY] Erro {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"❌ [ZUCPAY] Erro ao criar PIX: {e}")
            import traceback
            traceback.print_exc()
            return None

    def verificar_pagamento(self, transaction_id):
        try:
            print(f"🔍 [ZUCPAY] Verificando status da transação: {transaction_id}")
            response = requests.get(
                f"{self.base_url}/pix/status/{transaction_id}",
                headers=self.get_headers(),
                timeout=30
            )
            if response.status_code in [200, 201, 202]:
                result = response.json()
                if result.get("success"):
                    status = result.get("status", "pending")
                    print(f"✅ [ZUCPAY] Status da transação {transaction_id}: {status}")
                    if status == "completed":
                        return "paid"
                    elif status == "pending":
                        return "pending"
                    elif status == "failed":
                        return "failed"
                    else:
                        return "pending"
            else:
                print(f"❌ [ZUCPAY] Erro ao verificar {transaction_id}: {response.status_code}")
            return None
        except Exception as e:
            print(f"❌ [ZUCPAY] Erro ao verificar pagamento: {e}")
            return None

    def consultar_saldo(self):
        try:
            print(f"💰 [ZUCPAY] Consultando saldo da conta")
            response = requests.get(
                f"{self.base_url}/balance",
                headers=self.get_headers(),
                timeout=30
            )
            if response.status_code in [200, 201, 202]:
                result = response.json()
                if result.get("success") and result.get("data"):
                    data = result["data"]
                    return {
                        "balance": data.get("balance", 0),
                        "total_deposited": data.get("total_deposited", 0),
                        "total_withdrawn": data.get("total_withdrawn", 0),
                        "currency": data.get("currency", "BRL")
                    }
            return None
        except Exception as e:
            print(f"❌ [ZUCPAY] Erro ao consultar saldo: {e}")
            return None


def processar_pagamento_aprovado(user_id, valor, payment_id, plataforma):
    """Processa pagamento aprovado - adiciona saldo e atualiza histórico"""
    try:
        print(f"💰 [{plataforma}] Processando pagamento aprovado para usuário {user_id}")
        
        with open('settings/credenciais.json', 'r') as f:
            creds = json.load(f)
        
        bonus_pix = creds.get('bonus_pix', 0)
        bonus_pix_min = creds.get('bonus_pix_min', 0)
        
        saldo_adicional = float(valor)
        if float(valor) >= bonus_pix_min and bonus_pix > 0:
            bonus_valor = float(valor) * (bonus_pix / 100)
            saldo_adicional += bonus_valor
            print(f"🎁 [{plataforma}] Bônus aplicado: +R${bonus_valor:.2f}")
        
        InfoUser.add_saldo(user_id, saldo_adicional)
        print(f"✅ [{plataforma}] Saldo adicionado: +R${saldo_adicional:.2f}")
        
        porcentagem = AfiliadosInfo.porcentagem_por_indicacao()
        valor_indicacao = float(valor) * int(porcentagem) / 100
        
        MudancaHistorico.add_pagamentos(user_id, valor, payment_id, valor_indicacao)
        
        print(f"✅ [{plataforma}] Pagamento registrado no histórico")
        return True
    except Exception as e:
        print(f"❌ [{plataforma}] Erro ao processar pagamento: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== CLASSES AUXILIARES ====================
class ConverterMoeda:
    def conversao(quantidade):
        try:
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            api_key = data.get('api_awesomeapi', '')

            url = "https://economia.awesomeapi.com.br/last/USD-BRL"
            if api_key:
                url += f"?apiKey={api_key}"

            response = requests.get(url, timeout=5)
            data = response.json()
            
            if "USDBRL" in data and "high" in data["USDBRL"]:
                valor_dolar = f'{float(data["USDBRL"]["high"]):.3f}'
            elif "USDBRL" in data and "bid" in data["USDBRL"]:
                valor_dolar = f'{float(data["USDBRL"]["bid"]):.3f}'
            else:
                valor_dolar = "5.70"
                
        except Exception as e:
            valor_dolar = "5.20"
        
        return f'{float(quantidade) * float(valor_dolar)}'

class InfoApi:
    @staticmethod
    def comprar_numero(servico, pais, operadora: str | None = None, provedor_forcado=None, max_price=None, fixed_price=None):
        """Função UNIFICADA para comprar número"""
        print(f"🔄 [API COMPRAR_NUMERO] Função chamada")
        print(f"   └─ servico: {servico}")
        print(f"   └─ pais: {pais}")
        print(f"   └─ operadora: {operadora}")
        print(f"   └─ provedor_forcado: {provedor_forcado}")
        print(f"   └─ max_price: {max_price}")
        print(f"   └─ fixed_price: {fixed_price}")
        
        if max_price is not None:
            max_price = str(max_price)
        if fixed_price is not None:
            fixed_price = str(fixed_price)
            
        data = _ensure_sms_provider_migration()
        provider_config = provedor_forcado if provedor_forcado else str(data.get("sms_provider", "herosms")).strip().lower()

        print(f"⚙️ [API CONFIG] Provider config: {provider_config}")

        if provider_config == "todos":
            print(f"🔄 [API TODOS] Tentando múltiplos provedores")
            clients = sms_clients_all()
            if not clients:
                print(f"❌ [API TODOS] Nenhum provedor configurado")
                return {"error": "no_providers_configured"}

            falhas_por_provedor = {}

            for client in clients:
                try:
                    print(f"🔍 [API PROVEDOR] Tentando {client.provider}")
                    
                    prices = client.getPrices(servico, pais)
                    if isinstance(prices, dict) and str(pais) in prices:
                        servico_data = prices[str(pais)].get(str(servico), {})
                        estoque = servico_data.get("count", 0)
                        
                        if int(estoque) > 0:
                            print(f"✅ [API] {client.provider} tem {estoque} unidades")
                            compra = client.getNumberV2(servico, operator=operadora, country=pais, maxPrice=max_price, fixedPrice=fixed_price)
                            
                            if isinstance(compra, dict):
                                if "activationId" in compra and "phoneNumber" in compra:
                                    print(f"✅ [API SUCESSO] {client.provider} forneceu número")
                                    return {
                                        "id": compra["activationId"],
                                        "numero": compra["phoneNumber"],
                                        "operadora": compra.get("activationOperator") or None,
                                        "provedor": client.provider
                                    }
                                elif "error" in compra:
                                    error = compra["error"]
                                    print(f"❌ [API ERRO] {client.provider}: {error}")
                                    falhas_por_provedor[client.provider] = error
                                    if error in ["NO_BALANCE", "BAD_KEY", "NO_NUMBERS"]:
                                        continue
                            else:
                                print(f"❌ [API] {client.provider} retornou resposta inválida")
                                falhas_por_provedor[client.provider] = "RESPOSTA_INVALIDA"
                        else:
                            print(f"❌ [API] {client.provider} sem estoque")
                            falhas_por_provedor[client.provider] = "SEM_ESTOQUE"
                except Exception as e:
                    print(f"❌ [API EXCEPTION] {client.provider}: {e}")
                    falhas_por_provedor[client.provider] = f"EXCEPTION: {str(e)}"
                    continue

            print(f"❌ [API TODOS FALHARAM] Nenhum provedor conseguiu fornecer")
            return {"error": "no_stock_all_providers", "details": falhas_por_provedor}

        else:
            print(f"🎯 [API ESPECÍFICO] Usando provedor específico: {provider_config}")
            clients = sms_clients_all()
            client_forcado = None
            for client in clients:
                if client.provider == provider_config:
                    client_forcado = client
                    break

            if not client_forcado:
                print(f"❌ [API NÃO ENCONTRADO] Provedor '{provider_config}' não encontrado")
                return {"error": "provider_not_found"}

            try:
                prices = client_forcado.getPrices(servico, pais)
                if isinstance(prices, dict) and str(pais) in prices:
                    servico_data = prices[str(pais)].get(str(servico), {})
                    estoque = servico_data.get("count", 0)
                    
                    if int(estoque) == 0:
                        print(f"❌ [API] {client_forcado.provider} sem estoque")
                        return {"error": "no_stock"}
                    
                    print(f"🚀 [API COMPRA] Tentando comprar no {client_forcado.provider}")
                    compra = client_forcado.getNumberV2(
                        servico,
                        operator=operadora,
                        country=pais,
                        maxPrice=max_price,
                        fixedPrice=fixed_price
                    )
                    
                    print(f"📥 [API RESPOSTA] {client_forcado.provider}: {repr(compra)}")
                    
                    if isinstance(compra, dict):
                        if "activationId" in compra and "phoneNumber" in compra:
                            print(f"✅ [API SUCESSO] {client_forcado.provider} forneceu número")
                            return {
                                "id": compra["activationId"],
                                "numero": compra["phoneNumber"],
                                "operadora": compra.get("activationOperator") or None,
                                "provedor": client_forcado.provider
                            }
                        elif "error" in compra:
                            error = compra["error"]
                            print(f"❌ [API ERRO] {client_forcado.provider}: {error}")
                            if error == "NO_BALANCE":
                                return {"error": "insufficient_balance"}
                            elif error == "BAD_KEY":
                                return {"error": "invalid_api_key"}
                            elif error == "NO_NUMBERS":
                                return {"error": "no_stock"}
                            else:
                                return {"error": "api_error", "details": error}
                    else:
                        return {"error": "invalid_response"}
                else:
                    return {"error": "no_stock"}
            except Exception as e:
                print(f"❌ [API EXCEPTION] {client_forcado.provider}: {e}")
                return {"error": "api_error", "details": str(e)}

    @staticmethod
    def pegar_status_numero(id, provedor=None):
        """Versão CORRIGIDA com melhor tratamento de status"""
        try:
            if provedor:
                clients = sms_clients_all()
                client_especifico = None
                for client in clients:
                    if client.provider == provedor:
                        client_especifico = client
                        break
                if client_especifico:
                    status = client_especifico.getStatus(id)
                else:
                    print(f"⚠️ [STATUS API] Provedor {provedor} não encontrado, usando padrão")
                    status = sms.getStatus(id)
            else:
                status = sms.getStatus(id)

            print(f"📊 [STATUS RAW] ID:{id} | Status: {repr(status)}")

            if status is None:
                print(f"⚠️ [STATUS] API retornou None para ID: {id}")
                return "Aguardando SMS..."
            
            if isinstance(status, str):
                status_upper = status.upper()
                
                if status_upper == 'STATUS_CANCEL':
                    return False
                elif status_upper == 'STATUS_WAIT_CODE':
                    return 'Aguardando SMS...'
                elif status_upper.startswith('STATUS_WAIT_RETRY'):
                    return 'Aguardando reenvio...'
                elif status_upper == 'STATUS_WAIT_RESEND':
                    return 'Aguardando reenvio...'
                elif status_upper.startswith('STATUS_OK'):
                    partes = status.split(':', 1)
                    if len(partes) > 1:
                        codigo = partes[1].strip()
                        return f'<b>Novo código:</b> <code>{codigo}</code>'
                    return 'Código recebido (formato desconhecido)'
                elif len(status) > 0 and len(status) < 10 and status.isdigit():
                    return f'<b>Novo código:</b> <code>{status}</code>'
                else:
                    print(f"⚠️ [STATUS DESCONHECIDO] {repr(status)} - mantendo aguardando")
                    return 'Aguardando SMS...'
            else:
                print(f"⚠️ [STATUS TIPO INESPERADO] {type(status)} - {repr(status)}")
                return 'Aguardando SMS...'
                
        except Exception as e:
            print(f"❌ [STATUS ERRO] ID:{id} - {e}")
            return 'Aguardando SMS...'

    @staticmethod
    def mudar_status_numero(id, status, provedor=None):
        status_map = {
            "1": "informar sobre a prontidão do número",
            "3": "Solicite outro código (gratuito)",
            "6": "Ativação completa",
            "8": "informar que o número foi utilizado e cancelar a ativação"
        }

        if provedor:
            clients = sms_clients_all()
            client_especifico = None
            for client in clients:
                if client.provider == provedor:
                    client_especifico = client
                    break
            if client_especifico:
                mudanca = client_especifico.setStatus(id=str(id), status=str(status))
            else:
                print(f"⚠️ [PROVEDOR NÃO ENCONTRADO] {provedor}, usando provedor padrão")
                mudanca = sms.setStatus(id=str(id), status=str(status))
        else:
            mudanca = sms.setStatus(id=str(id), status=str(status))

        return mudanca

    @staticmethod
    def comparativo(entrada):
        ofertas = []
        resp = sms.getTopCountriesByService(f'{entrada}')
        if isinstance(resp, dict) and "error" not in resp:
            try:
                for _, item in resp.items():
                    if isinstance(item, dict) and "country" in item and "price" in item:
                        ofertas.append({"pais": item["country"], "valor": float(item["price"])})
            except Exception:
                ofertas = []

        if not ofertas:
            with open('infosms/paises.json', 'r') as f:
                arquivo = json.load(f)
            for pais in arquivo.get("pais", []):
                pais_id = str(pais.get("id"))
                try:
                    precos = sms.getPrices(str(entrada), pais_id)
                    if isinstance(precos, dict) and pais_id in precos and str(entrada) in precos[pais_id]:
                        info = precos[pais_id][str(entrada)]
                        count = int(info.get("count", 0))
                        cost = float(info.get("cost", 0))
                        if count > 0 and cost > 0:
                            ofertas.append({"pais": pais_id, "valor": cost})
                except Exception:
                    pass

        lista_ordenada = sorted(ofertas, key=lambda x: x["valor"])[:20]
        response = []
        for oferta in lista_ordenada:
            try:
                pais_id = oferta["pais"]
                pais = InfoApi.pegar_pais(pais_id)
                valor = InfoApi.pegar_servico(pais_id, str(entrada))
                valor = valor["valor"]
                if str(pais_id) == '73':
                    with open('settings/substituir_valor.json', 'r') as f:
                        data = json.load(f)
                    for servico_mod in data["servicos"]:
                        if str(entrada) == servico_mod["id"]:
                            valor = float(servico_mod["valor"])
                            break
                response.append({"id": pais_id, "pais": pais, "valor": float(valor)})
            except Exception as e:
                print(e)
        return response
    
    @staticmethod
    def api_sms():
        data = _ensure_sms_provider_migration()
        provider = str(data.get("sms_provider", "herosms")).strip().lower()
        if provider == "grizzly":
            return str(data.get("api-sms-grizzly", "")).strip()
        return str(data.get("api-sms-herosms", "")).strip()
    
    @staticmethod
    def porcentagem_lucro():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        return data["porcentagem-lucro"]

    @staticmethod
    def obter_cotacao_dolar():
        try:
            with open('settings/credenciais.json', 'r') as f:
                creds = json.load(f)
            api_key = creds.get('api_awesomeapi', '')

            url = "https://economia.awesomeapi.com.br/last/USD-BRL"
            if api_key:
                url += f"?apiKey={api_key}"

            response = requests.get(url, timeout=5)
            data = response.json()

            if "USDBRL" in data and "high" in data["USDBRL"]:
                cotacao_dolar1 = f'{float(data["USDBRL"]["high"]):.3f}'
            elif "USDBRL" in data and "bid" in data["USDBRL"]:
                cotacao_dolar1 = f'{float(data["USDBRL"]["bid"]):.3f}'
            else:
                cotacao_dolar1 = "5.70"

        except Exception as e:
            cotacao_dolar1 = "5.70"

        return float(cotacao_dolar1)
    
    @staticmethod
    def mudar_porcentagem_lucro(porcent):
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["porcentagem-lucro"] = porcent
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
    
    @staticmethod
    def saldo_api():
        return sms.getBalance()
    
    @staticmethod
    def operadoras():
        lista = ['claro', 'oi', 'tim', 'vivo']
        return lista
    
    @staticmethod
    def mudar_nomes_servicos(nome):
        try:
            with open('settings/traducoes_servicos.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            traducao = data["traducoes"].get(nome, None)
            return traducao
        except Exception as e:
            print(f"Erro ao carregar traduções de serviços: {e}")
            return None
    
    @staticmethod
    def obter_id_servico(nome_servico):
        try:
            with open('settings/traducoes_servicos.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            for id_servico, nome in data["traducoes"].items():
                if nome.lower() == nome_servico.lower():
                    return id_servico
            return None
        except Exception as e:
            print(f"Erro ao obter ID do serviço: {e}")
            return None
    
    @staticmethod
    def tem_traducao(nome):
        return InfoApi.mudar_nomes_servicos(nome) is not None
    
    @staticmethod
    def servicos(pais, operadora: str | None = None):
        lista = []
        
        try:
            all_services = sms.getPrices("", pais)
            if pais in all_services:
                ls = all_services[pais]
            else:
                print(f"País {pais} não encontrado nos serviços")
                return []
        except Exception as e:
            print(f"Erro ao obter serviços do país {pais}: {e}")
            return []
        
        porcentagem_lucro = InfoApi.porcentagem_lucro()
        cotacao_dolar = InfoApi.obter_cotacao_dolar()
        
        for serv in ls:
            id = serv
            count = ls[serv].get("count", 0)
            custo = ls[serv].get("cost", 0)
            
            custo_real1 = float(custo) * float(cotacao_dolar)
            custo_real = f'{float(custo_real1):.2f}'
            
            if float(custo_real) < 0.01:
                custo_real = "0.01"
            
            search_name = ls[serv].get("search_name", f"Serviço {id}")
            name = search_name.split(',')[0].split('/')[0].split('+')[0]
            
            if not InfoApi.tem_traducao(id) and not InfoApi.tem_traducao(name.lower()):
                continue
            
            name_teste = InfoApi.mudar_nomes_servicos(id)
            if name_teste == None:
                name_teste = InfoApi.mudar_nomes_servicos(name.lower())
                if name_teste == None:
                    continue
                else:
                    name = name_teste
            else:
                name = name_teste
                
            valor = float(custo_real) * float(porcentagem_lucro) / 100
            valor = f'{float(valor + float(custo_real)):.2f}'
            if str(pais) == '73':
                try:
                    with open('settings/credenciais.json', 'r') as f:
                        cred_data = json.load(f)
                    usar_precos_fixos = cred_data.get("usar_precos_fixos_brasil", False)
                    
                    if usar_precos_fixos:
                        with open('settings/substituir_valor.json', 'r') as f:
                            data = json.load(f)
                        for servico_mod in data["servicos"]:
                            if id == servico_mod["id"]:
                                valor = float(servico_mod["valor"])
                                break
                except Exception as e:
                    print(f"Erro ao verificar configuração de preços fixos: {e}")
            servico = {"id": id, "nome": name, "valor": valor}
            lista.append(servico)
        return lista
    
    @staticmethod
    def pegar_servico(pais, id):
        servico = None
        
        try:
            print(f"[TENTANDO getPrices] pais={pais}, id={id}")
            info_servico2 = sms.getPrices(id, pais)
            if not isinstance(info_servico2, dict):
                print(f"[AVISO] getPrices retornou resposta inválida (não é dict): {info_servico2}")
                info_servico2 = None
            
            if info_servico2 and pais in info_servico2 and id in info_servico2[pais]:
                info_servico1 = info_servico2[pais][id]
                count = info_servico1.get("count", 0)
                custo = info_servico1.get("cost", 0)
                
                porcentagem_lucro = InfoApi.porcentagem_lucro()
                cotacao_dolar = InfoApi.obter_cotacao_dolar()
                
                custo_real1 = float(custo) * float(cotacao_dolar)
                custo_real = f'{float(custo_real1):.2f}'
                
                if float(custo_real) < 0.01:
                    custo_real = "0.01"
                valor = float(custo_real) * float(porcentagem_lucro) / 100
                valor = f'{float(valor + float(custo_real)):.2f}'
                
                if not InfoApi.tem_traducao(id):
                    return None
                
                name = f"Serviço {id}"
                name_teste = InfoApi.mudar_nomes_servicos(id)
                if name_teste != None:
                    name = name_teste
                
                if str(pais) == '73':
                    try:
                        with open('settings/credenciais.json', 'r') as f:
                            cred_data = json.load(f)
                        usar_precos_fixos = cred_data.get("usar_precos_fixos_brasil", False)
                        
                        if usar_precos_fixos:
                            with open('settings/substituir_valor.json', 'r') as f:
                                data = json.load(f)
                            for servico_mod in data["servicos"]:
                                if id == servico_mod["id"]:
                                    valor = float(servico_mod["valor"])
                                    break
                    except Exception as e:
                        print(f"Erro ao verificar configuração de preços fixos: {e}")
                
                servico = {"id": id, "nome": name, "valor": valor, "count": count}
                return servico
        except Exception as e:
            print(f"Erro ao obter serviço {id} no país {pais}: {e}")
        
        try:
            print(f"[TENTANDO getRentServicesAndCountries] pais={pais}")
            ls = sms.getRentServicesAndCountries(country=str(pais))
            if not isinstance(ls, dict):
                print(f"[AVISO] getRentServicesAndCountries retornou resposta inválida (não é dict): {ls}")
                ls = None
            
            if ls and "services" in ls and id in ls["services"]:
                info_servico = ls["services"][id]
                count = info_servico.get("count", 0)
                custo = info_servico.get("cost", 0)
                
                porcentagem_lucro = InfoApi.porcentagem_lucro()
                cotacao_dolar = InfoApi.obter_cotacao_dolar()
                
                custo_real1 = float(custo) * float(cotacao_dolar)
                custo_real = f'{float(custo_real1):.2f}'
                
                if float(custo_real) < 0.01:
                    custo_real = "0.01"
                valor = float(custo_real) * float(porcentagem_lucro) / 100
                valor = f'{float(valor + float(custo_real)):.2f}'
                
                search_name = info_servico.get("search_name", f"Serviço {id}")
                name = search_name.split(',')[0].split('/')[0].split('+')[0]
                
                name_teste = InfoApi.mudar_nomes_servicos(id)
                if name_teste == None:
                    name_teste = InfoApi.mudar_nomes_servicos(name.lower())
                    if name_teste == None:
                        return None
                    else:
                        name = name_teste
                else:
                    name = name_teste
                
                if str(pais) == '73':
                    try:
                        with open('settings/credenciais.json', 'r') as f:
                            cred_data = json.load(f)
                        usar_precos_fixos = cred_data.get("usar_precos_fixos_brasil", False)
                        
                        if usar_precos_fixos:
                            with open('settings/substituir_valor.json', 'r') as f:
                                data = json.load(f)
                            for servico_mod in data["servicos"]:
                                if id == servico_mod["id"]:
                                    valor = float(servico_mod["valor"])
                                    break
                    except Exception as e:
                        print(f"Erro ao verificar configuração de preços fixos: {e}")
                
                servico = {"id": id, "nome": name, "valor": valor, "count": count}
                return servico
        except Exception as e:
            print(f"Erro ao obter serviço de aluguel {id} no país {pais}: {e}")
        
        print(f"[FALHA FINAL] pegar_servico retornando None para id={id}, pais={pais}")
        return None
    
    @staticmethod
    def listar_pais():
        with open('infosms/paises.json', 'r') as f:
            data = json.load(f)
        return data["pais"]
    
    @staticmethod
    def pegar_pais(id):
        with open('infosms/paises.json', 'r') as f:
            data = json.load(f)["pais"]
        for pais in data:
            if str(pais["id"]) == str(id):
                return pais["pais"]
        return False

class ApiGnInfo:
    @staticmethod
    def saldo():
        response = gn.pix_list_balance()
        saldo = response["saldo"]
        return f'{float(saldo):.2f}'
    
    @staticmethod
    def extrato():
        data_atual = datetime.now()
        fuso_horario = timezone('America/Sao_Paulo')
        data_de_hoje = data_atual.astimezone(fuso_horario)
        data_fim = data_de_hoje.strftime('%Y-%m-%d')
        data_inicio = data_de_hoje.strftime('%Y-%m-01')
        params = {
            "inicio": f"{data_inicio}T21:00:00Z",
            "fim": f"{data_fim}T20:59:00Z"
        }
        response = gn.pix_list_charges(params=params)
        return response
    
    @staticmethod
    def pix_gerados():
        response = ApiGnInfo.extrato()
        quantity = 0
        for cobranca in response["cobs"]:
            if cobranca["status"] != 'CONCLUIDA':
                quantity += 1
        return quantity
    
    @staticmethod
    def pix_pagos():
        response = ApiGnInfo.extrato()
        quantity = 0
        for cobranca in response["cobs"]:
            if cobranca["status"] == 'CONCLUIDA':
                quantity += 1
        return quantity
    
    @staticmethod
    def txt_detalhado_pix_gerados():
        response = ApiGnInfo.extrato()
        ord_limpa = []
        for cobranca in response["cobs"]:
            if cobranca["status"] != 'CONCLUIDA':
                ord_limpa.append(cobranca)
        texto = 'ÚLTIMOS 10 PIX GERADOS NA SUA CONTA GN\n\n'
        for cobranca in ord_limpa[:10]:
            horario_gerado = cobranca["calendario"]["criacao"]
            valor = cobranca["valor"]["original"]
            id_pag = cobranca["txid"]
            texto += f'Valor: R${valor}\nData: {horario_gerado}\nTransation ID: {id_pag}\n\n\n'
        with open('pix_gerados_gn.txt', 'w') as f:
            f.write(texto)
        return 'pix_gerados_gn'
    
    @staticmethod
    def txt_detalhado_pix_pagos():
        response = ApiGnInfo.extrato()
        ord_limpa = []
        for cobranca in response["cobs"]:
            if cobranca["status"] == 'CONCLUIDA':
                ord_limpa.append(cobranca)
        texto = 'ÚLTIMOS 10 PIX PAGOS NA SUA CONTA GN\n\n'
        for cobranca in ord_limpa[:10]:
            try:
                if cobranca["loc"]["tipoCob"] == 'cob':
                    gerado_pela_api = 'Sim'
                else:
                    gerado_pela_api = 'Não'
            except:
                gerado_pela_api = 'Não'
            horario_gerado = cobranca["calendario"]["criacao"]
            valor = cobranca["valor"]["original"]
            id_pag = cobranca["txid"]
            texto += f'Valor: R${valor}\nData: {horario_gerado}\nTransation ID: {id_pag}\nGerado pela api: {gerado_pela_api}\n\n\n'
        with open('pix_pagos_gn.txt', 'w') as f:
            f.write(texto)
        return 'pix_pagos_gn'

class ViewTime:
    @staticmethod
    def data_atual():
        from datetime import datetime
        data_atual = datetime.now()
        fuso_horario = timezone('America/Sao_Paulo')
        data_sao_paulo = data_atual.astimezone(fuso_horario)
        data_em_texto = data_sao_paulo.strftime('%d/%m/%Y')
        return data_em_texto
    
    @staticmethod
    def hora_atual():
        from datetime import datetime
        data_e_hora_atuais = datetime.now()
        fuso_horario = timezone('America/Sao_Paulo')
        data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
        hora_sao_paulo_em_texto = data_e_hora_sao_paulo.strftime('%H:%M:%S')
        hora_sao_paulo = datetime.strptime(hora_sao_paulo_em_texto, '%H:%M:%S').time()
        return hora_sao_paulo

class MetricasVendas:
    @staticmethod
    def total():
        data = _load_users_json_safe()["users"]
        receita = 0
        gasto = 0
        for user in data:
            for compra in user["compras"]:
                receita += float(compra["valor"])
                valor = float(compra["valor"])
                per = float(InfoApi.porcentagem_lucro())
                soma = valor - (valor * per / 100)
                gasto += soma
        return {"receita": f'{float(receita):.2f}', "gasto": f'{float(gasto):.2f}'}
    
    @staticmethod
    def trinta():
        data = _load_users_json_safe()["users"]
        receita = 0
        gasto = 0
        for user in data:
            for compra in user["compras"]:
                data_compra = compra["data"].split(' ')[0]
                data_atual = datetime.now()
                fuso_horario = timezone('America/Sao_Paulo')
                data_sao_paulo = data_atual.astimezone(fuso_horario)
                data_em_texto = data_sao_paulo.strftime('%d/%m/%Y')
                dia_de_hoje = datetime.strptime(data_em_texto, '%d/%m/%Y')
                dia_comprado = datetime.strptime(data_compra, '%d/%m/%Y')
                if (dia_de_hoje - dia_comprado).days < 30:
                    receita += float(compra["valor"])
                    valor = float(compra["valor"])
                    per = float(InfoApi.porcentagem_lucro())
                    soma = valor - (valor * per / 100)
                    gasto += soma
        return {"receita": f'{float(receita):.2f}', "gasto": f'{float(gasto):.2f}'}
    
    @staticmethod
    def sete():
        data = _load_users_json_safe()["users"]
        receita = 0
        gasto = 0
        for user in data:
            for compra in user["compras"]:
                data_compra = compra["data"].split(' ')[0]
                data_atual = datetime.now()
                fuso_horario = timezone('America/Sao_Paulo')
                data_sao_paulo = data_atual.astimezone(fuso_horario)
                data_em_texto = data_sao_paulo.strftime('%d/%m/%Y')
                dia_de_hoje = datetime.strptime(data_em_texto, '%d/%m/%Y')
                dia_comprado = datetime.strptime(data_compra, '%d/%m/%Y')
                if (dia_de_hoje - dia_comprado).days < 7:
                    receita += float(compra["valor"])
                    valor = float(compra["valor"])
                    per = float(InfoApi.porcentagem_lucro())
                    soma = valor - (valor * per / 100)
                    gasto += soma
        return {"receita": f'{float(receita):.2f}', "gasto": f'{float(gasto):.2f}'}
    
    @staticmethod
    def hoje():
        data = _load_users_json_safe()["users"]
        receita = 0
        gasto = 0
        for user in data:
            for compra in user["compras"]:
                data_compra = compra["data"].split(' ')[0]
                data_atual = datetime.now()
                fuso_horario = timezone('America/Sao_Paulo')
                data_sao_paulo = data_atual.astimezone(fuso_horario)
                data_em_texto = data_sao_paulo.strftime('%d/%m/%Y')
                dia_de_hoje = datetime.strptime(data_em_texto, '%d/%m/%Y')
                dia_comprado = datetime.strptime(data_compra, '%d/%m/%Y')
                if dia_de_hoje == dia_comprado:
                    receita += float(compra["valor"])
                    valor = float(compra["valor"])
                    per = float(InfoApi.porcentagem_lucro())
                    soma = valor - (valor * per / 100)
                    gasto += soma
        return {"receita": f'{float(receita):.2f}', "gasto": f'{float(gasto):.2f}'}

# ==================== CREDENTIALS CHANGE (mantido igual) ====================
class CredentialsChange:
    @staticmethod
    def user_bot():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        return str(data["user_bot"])
    
    @staticmethod
    def mudar_user_bot(user):
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["user_bot"] = str(user)
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
    
    @staticmethod
    def token_bot():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        return str(data["api-bot"])
    
    @staticmethod
    def mudar_token_bot(token):
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["api-bot"] = str(token)
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
    
    @staticmethod
    def obter_versao_bot():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        return data.get("version", "1.0")
    
    @staticmethod
    def mudar_versao_bot(version):
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["version"] = version
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
    
    @staticmethod
    def verificar_premium():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
            return data["premium"]
    
    @staticmethod
    def separador():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        return str(data["separador"])
    
    @staticmethod
    def mudar_separador(separador):
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["separador"] = separador
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
    
    @staticmethod
    def status_manutencao():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        if data["maintance"] == 'on':
            return True
        else:
            return False
    
    @staticmethod
    def mudar_status_manutencao():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        if data["maintance"] == "on":
            data["maintance"] = "off"
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
                return
        else:
            data["maintance"] = "on"
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
                return
    
    @staticmethod
    def id_dono():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        dono_id = data["id_dono"]
        return int(dono_id)
    
    @staticmethod
    def mudar_dono(id: str | int):
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["id_dono"] = int(id)
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
    
    @staticmethod
    def tempo_expiracao_sms():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        return int(data.get("tempo_expiracao_sms", 15))
    
    class VerificacaoCanal:
        @staticmethod
        def status_verificacao():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            if data["verificacao_canal"] == 'on':
                return True
            else:
                return False
        
        @staticmethod
        def mudar_status_verificacao():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            if data["verificacao_canal"] == "on":
                data["verificacao_canal"] = "off"
            else:
                data["verificacao_canal"] = "on"
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
        
        @staticmethod
        def id_canal():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            return data["id_canal_verificacao"]
        
        @staticmethod
        def mudar_id_canal(id_canal):
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            data["id_canal_verificacao"] = str(id_canal)
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
        
        @staticmethod
        def link_canal():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            return data["link_canal_verificacao"]
        
        @staticmethod
        def mudar_link_canal(link):
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            data["link_canal_verificacao"] = str(link)
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
        
        @staticmethod
        def verificar_membro_canal(user_id, bot_token):
            try:
                print(f"[VERIFICAÇÃO CANAL API] user_id: {user_id}")
                
                with open('settings/credenciais.json', 'r') as f:
                    data = json.load(f)
                
                status_verif = data.get("verificacao_canal", "off")
                if status_verif != 'on':
                    return True
                
                id_canal = data.get("id_canal_verificacao", "")
                if not id_canal or id_canal in ["", "None", "none", "0"]:
                    return True
                
                url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
                params = {
                    "chat_id": id_canal,
                    "user_id": user_id
                }
                
                response = requests.get(url, params=params, timeout=10)
                result_data = response.json()
                
                if result_data.get("ok"):
                    status = result_data.get("result", {}).get("status", "")
                    is_member = status in ["member", "administrator", "creator"]
                    
                    if is_member:
                        print(f"✅ Usuário {user_id} É MEMBRO")
                        return True
                    else:
                        print(f"❌ Usuário {user_id} NÃO É MEMBRO")
                        return False
                else:
                    print(f"❌ Erro da API: {result_data.get('description')}")
                    return False
                    
            except Exception as e:
                print(f"❌ Erro na verificação: {e}")
                return False
        
        @staticmethod
        def status_notificacao():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            if data.get("notificacao_canal", "off") == 'on':
                return True
            else:
                return False
        
        @staticmethod
        def mudar_status_notificacao():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            if "notificacao_canal" not in data:
                data["notificacao_canal"] = "off"
            if data["notificacao_canal"] == "on":
                data["notificacao_canal"] = "off"
            else:
                data["notificacao_canal"] = "on"
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
    
    class PlataformaPix:
        @staticmethod
        def status_zucpay():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            if data.get("status-pix-zucpay", True) == True:
                return True
            else:
                return False
        
        @staticmethod
        def mudar_status_zucpay():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            if data.get("status-pix-zucpay", False) == False:
                data["status-pix-zucpay"] = True
            else:
                data["status-pix-zucpay"] = False
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
        
        @staticmethod
        def plataforma_padrao():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            return data.get("plataforma_pagamento_padrao", "zucpay")
        
        @staticmethod
        def mudar_plataforma_padrao(plataforma):
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            data["plataforma_pagamento_padrao"] = plataforma
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
    
    class FotoMenu:
        @staticmethod
        def foto_atual():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            return data["foto-menu"]
        
        @staticmethod
        def mudar_foto_atual(url):
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            data["foto-menu"] = url
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
    
    class SuporteInfo:
        @staticmethod
        def link_suporte():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            return str(data["link_suporte"])
        
        @staticmethod
        def mudar_link_suporte(link):
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            data["link_suporte"] = str(link)
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
    
    class StatusPix:
        @staticmethod
        def pix_manual():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            if str(data["status_pix_manu"]) == 'on':
                return True
            else:
                return False
        
        @staticmethod
        def pix_auto():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            if str(data["status_pix_auto"]) == 'on':
                return True
            else:
                return False
    
    class ChangeStatusPix:
        @staticmethod
        def change_pix_manual():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            if str(data["status_pix_manu"]) == 'on':
                data["status_pix_manu"] = 'off'
                with open('settings/credenciais.json', 'w') as f:
                    json.dump(data, f, indent=4)
                return
            else:
                data["status_pix_manu"] = 'on'
                with open('settings/credenciais.json', 'w') as f:
                    json.dump(data, f, indent=4)
                return False
        
        @staticmethod
        def change_pix_auto():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            if str(data["status_pix_auto"]) == 'on':
                data["status_pix_auto"] = 'off'
                with open('settings/credenciais.json', 'w') as f:
                    json.dump(data, f, indent=4)
                return
            else:
                data["status_pix_auto"] = 'on'
                with open('settings/credenciais.json', 'w') as f:
                    json.dump(data, f, indent=4)
                return False
    
    class BonusPix:
        @staticmethod
        def quantidade_bonus():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            return int(data["bonus_pix"])
        
        @staticmethod
        def mudar_quantidade_bonus(porcentagem):
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            data["bonus_pix"] = int(porcentagem)
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
                return
        
        @staticmethod
        def valor_minimo_para_bonus():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            return int(data["bonus_pix_min"])
        
        @staticmethod
        def mudar_valor_minimo_para_bonus(valor_min):
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            data["bonus_pix_min"] = int(valor_min)
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
    
    class BonusRegistro:
        @staticmethod
        def bonus():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            return float(data["bonus_registro"])
        
        @staticmethod
        def mudar_bonus(novo_bonus):
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            data["bonus_registro"] = float(novo_bonus)
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
    
    class InfoPix:
        @staticmethod
        def token_zucpay():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            return str(data.get("token_zucpay", ""))
        
        @staticmethod
        def deposito_minimo_pix():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            return float(data.get("min_pix", 3.0))
        
        @staticmethod
        def trocar_deposito_minimo_pix(min):
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            data["min_pix"] = float(min)
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
        
        @staticmethod
        def deposito_maximo_pix():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            return float(data.get("max_pix", 2000.0))
        
        @staticmethod
        def trocar_deposito_maximo_pix(max):
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            data["max_pix"] = float(max)
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
        
        @staticmethod
        def expiracao():
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            return int(data.get("expiracao_pix", 20))
        
        @staticmethod
        def mudar_expiracao(minutes):
            with open('settings/credenciais.json', 'r') as f:
                data = json.load(f)
            data["expiracao_pix"] = int(minutes)
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
                return True

class ServicosDestaque():
    def obter_servicos_destaque():
        try:
            with open('settings/servicos_destaque.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("servicos_destaque", [])
        except Exception as e:
            print(f"Erro ao ler serviços em destaque: {e}")
            return []
    
    def adicionar_servico_destaque(nome_servico):
        try:
            with open('settings/servicos_destaque.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if nome_servico not in data["servicos_destaque"]:
                data["servicos_destaque"].append(nome_servico)
                
                with open('settings/servicos_destaque.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                return True
            return False
        except Exception as e:
            print(f"Erro ao adicionar serviço em destaque: {e}")
            return False
    
    def remover_servico_destaque(nome_servico):
        try:
            with open('settings/servicos_destaque.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if nome_servico in data["servicos_destaque"]:
                data["servicos_destaque"].remove(nome_servico)
                
                with open('settings/servicos_destaque.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                return True
            return False
        except Exception as e:
            print(f"Erro ao remover serviço em destaque: {e}")
            return False

class AfiliadosInfo():
    def status_afiliado():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        if data["afiliados"] == 'on':
            return True
        else:
            return False
    def mudar_status_afiliado():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        if data["afiliados"] == 'on':
            data["afiliados"] = "off"
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)
            return
        else:
            data["afiliados"] = "on"
            with open('settings/credenciais.json', 'w') as f:
                json.dump(data, f, indent=4)

        return
    def porcentagem_por_indicacao():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        return int(data["pontos_by_indicate_buy"])
    def mudar_porcentagem_por_indicacao(pontos):
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["pontos_by_indicate_buy"] = int(pontos)
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
        return
    def minimo_pontos_pra_saldo():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        return data["min_points_saldo"]
    def trocar_minimo_pontos_pra_saldo(min):
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["min_points_saldo"] = int(min)
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)
    def multiplicador_pontos():
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        return float(data["multiplicador_pontos"])
    def trocar_multiplicador_pontos(multiplicador):
        with open('settings/credenciais.json', 'r') as f:
            data = json.load(f)
        data["multiplicador_pontos"] = float(multiplicador)
        with open('settings/credenciais.json', 'w') as f:
            json.dump(data, f, indent=4)

class Notificacoes():
    def modo_servico():
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        return int(data["tipo_texto"])
    def mudar_modo_servico():
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        if data["tipo_texto"] == 0:
            data["tipo_texto"] = 1
        else:
            data["tipo_texto"] = 0
        with open('settings/notify.json', 'w') as f:
            json.dump(data, f, indent=4)
    def status_notificacoes():
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        if data["status_notify"] == 'on':
            return True
        else:
            return False
    def mudar_status_notificacoes():
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        if data["status_notify"] == 'on':
            data["status_notify"] = 'off'
            with open('settings/notify.json', 'w') as f:
                json.dump(data, f, indent=4)
            return
        else:
            data["status_notify"] = 'on'
            with open('settings/notify.json', 'w') as f:
                json.dump(data, f, indent=4)
            return
    def id_grupo():
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        return int(data["id_grupo"])
    def trocar_id_grupo(id_grupo):
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        data["id_grupo"] = int(id_grupo)
        with open('settings/notify.json', 'w') as f:
            json.dump(data, f, indent=4)
        return
    def tempo_minimo_compras():
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        return int(data["time_min_compras"])
    def quantidade_de_servicos_pra_sortear():
        with open('settings/notificacao/servicos.txt', 'r', encoding='utf-8') as f:
            file = f.read()
        quantidade = 0
        servicos = file.strip().split('\n')
        for servico in servicos:
            if len(servico) > 0:
                quantidade += 1
            pass
        return quantidade
    def pegar_servico_random():
        with open('settings/notificacao/servicos.txt', 'r', encoding='utf-8') as f:
            file = f.read()
        file = file.splitlines()
        servico = random.choice(file)
        separar = servico.strip().split('R$')
        servico = separar[0]
        valor = separar[1]
        return servico, f'R${valor}'
    def pegar_servicos_disponiveis():
        with open('database/acessos.json', 'r') as f:
            data = json.load(f)
        nomes = []
        for acesso in data["acessos"]:
            if acesso["nome"] in nomes:
                pass
            nomes.append({"nome": acesso["nome"], "valor": acesso["valor"]})
        sort = random.choice(nomes)
        return sort["nome"], f'R${sort["valor"]:.2f}'
    def mudar_servicos_random(lista):
        with open('settings/notificacao/servicos.txt', 'w', encoding='utf-8') as f:
            f.write(lista)
    def trocar_tempo_minimo_compras(min):
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        data["time_min_compras"] = int(min)
        with open('settings/notify.json', 'w') as f:
            json.dump(data, f, indent=4)
    def tempo_maximo_compras():
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        return int(data["time_max_compras"])
    def trocar_tempo_maximo_compras(max):
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        data["time_max_compras"] = int(max)
        with open('settings/notify.json', 'w') as f:
            json.dump(data, f, indent=4)
    def tempo_minimo_saldo():
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        return int(data["time_min_saldo"])
    def trocar_tempo_minimo_saldo(min):
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        data["time_min_saldo"] = int(min)
        with open('settings/notify.json', 'w') as f:
            json.dump(data, f, indent=4)
    def tempo_maximo_saldo():
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        return int(data["time_max_saldo"])
    def trocar_tempo_maximo_saldo(max):
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        data["time_max_saldo"] = int(max)
        with open('settings/notify.json', 'w') as f:
            json.dump(data, f, indent=4)
    def min_max_saldo():
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        return float(data["saldo_min"]), float(data["saldo_max"])
    def trocar_min_max_saldo(min, max):
        with open('settings/notify.json', 'r') as f:
            data = json.load(f)
        data["saldo_min"] = int(min)
        data["saldo_max"] = int(max)
        with open('settings/notify.json', 'w') as f:
            json.dump(data, f, indent=4)
    def pegar_texto_saldo():
        with open('settings/notificacao/saldo.txt', 'r', encoding='utf-8') as f:
            return f.read()
    def mudar_texto_saldo(texto):
        with open('settings/notificacao/saldo.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def pegar_texto_compra():
        with open('settings/notificacao/compra.txt', 'r', encoding='utf-8') as f:
            return f.read()
    def mudar_texto_compra(texto):
        with open('settings/notificacao/compra.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def texto_notificacao_saldo():
        texto = Notificacoes.pegar_texto_saldo()
        id = random.randint(898012903, 4290812093)
        saldo_min, saldo_max = Notificacoes.min_max_saldo()
        saldo =  random.randint(int(saldo_min), int(saldo_max))
        texto = texto.replace('{id}', f'{id}').replace('{saldo}', f'{saldo}')
        return texto
    def texto_notificacao_compra():
        texto = Notificacoes.pegar_texto_compra()
        id = random.randint(898012903, 4290812093)
        if Notificacoes.modo_servico() == 0:
            servico, valor = Notificacoes.pegar_servico_random()
        else:
            servico, valor = Notificacoes.pegar_servicos_disponiveis()
        texto = texto.replace('{id}', f'{id}').replace('{servico}', f'{servico}').replace('{valor}', f'{valor}')
        return texto

# ==================== CONTADOR DE MENSAGENS DO ADMIN (NOVO) ====================
class ContadorAdminMensagens:
    ARQUIVO = 'admin_message_counter.json'

    @staticmethod
    def _carregar():
        try:
            with open(ContadorAdminMensagens.ARQUIVO, 'r') as f:
                return json.load(f)
        except:
            return {'data': None, 'enviadas': 0, 'erros': 0, 'total': 0}

    @staticmethod
    def _salvar(data):
        with open(ContadorAdminMensagens.ARQUIVO, 'w') as f:
            json.dump(data, f)

    @staticmethod
    def incrementar_envio(sucesso=True):
        """Incrementa o contador de mensagens do admin para o dia atual."""
        hoje = datetime.now().strftime('%Y-%m-%d')
        dados = ContadorAdminMensagens._carregar()

        if dados.get('data') != hoje:
            dados = {'data': hoje, 'enviadas': 0, 'erros': 0, 'total': 0}

        dados['total'] += 1
        if sucesso:
            dados['enviadas'] += 1
        else:
            dados['erros'] += 1

        ContadorAdminMensagens._salvar(dados)

    @staticmethod
    def obter_stats():
        """Retorna estatísticas do dia atual."""
        dados = ContadorAdminMensagens._carregar()
        hoje = datetime.now().strftime('%Y-%m-%d')

        if dados.get('data') != hoje:
            return {'enviadas': 0, 'erros': 0, 'total': 0, 'sucesso': 0}

        enviadas = dados.get('enviadas', 0)
        erros = dados.get('erros', 0)
        total = enviadas + erros
        sucesso = (enviadas / total * 100) if total > 0 else 0

        return {
            'enviadas': enviadas,
            'erros': erros,
            'total': total,
            'sucesso': f'{sucesso:.1f}'
        }

# ==================== RANKING ====================
bot = telebot.TeleBot(CredentialsChange.token_bot())

class Ranking():
    def SmsRecebido():
        data = _load_users_json_safe()
        response = []
        processed_users = set()
        for user in data["users"]:
            if len(user["compras"]) != 0:
                compras = 0
                for compra in user["compras"]:
                    data_compra = compra["data"].split(' ')[0]
                    dateoi = datetime.now()
                    if dateoi.month == int(data_compra.split('/')[1]):
                        compras +=1
                if compras > 0 and user["id"] not in processed_users:
                    processed_users.add(user["id"])
                    try:
                        nome_user = bot.get_chat(user["id"]).first_name
                    except Exception:
                        nome_user = str(user['id'])
                    response.append({"nome": nome_user, "id": user["id"], "compras": compras})
        lista_ordenada = sorted(response, key=lambda x: -x["compras"])[:10]
        return lista_ordenada
    def Recarga():
        data = _load_users_json_safe()
        response = []
        processed_users = set()
        for user in data["users"]:
            if int(user["total_pagos"]) != 0:
                valor_em_recarga = 0
                for recarga in user["pagamentos"]:
                    data_compra = recarga["data"].split(' ')[0]
                    dateoi = datetime.now()
                    if dateoi.month == int(data_compra.split('/')[1]):
                        valor_em_recarga += float(recarga["valor"])
                if valor_em_recarga > 0 and user["id"] not in processed_users:
                    processed_users.add(user["id"])
                    try:
                        nome_user = bot.get_chat(user["id"]).first_name
                    except Exception:
                        nome_user = str(user['id'])
                    response.append({"nome": nome_user, "recargas": valor_em_recarga})
        lista_ordenada = sorted(response, key=lambda x: -x["recargas"])[:10]
        return lista_ordenada
    def Gift():
        data = _load_users_json_safe()
        response = []
        processed_users = set()
        for user in data["users"]:
            if len(user["gift_redeemed"]) != 0:
                valores_resgatados = 0
                for resgate in user["gift_redeemed"]:
                    data_compra = resgate["data"].split(' ')[0]
                    dateoi = datetime.now()
                    if dateoi.month == int(data_compra.split('/')[1]):
                        valores_resgatados += float(resgate["valor"])
                if valores_resgatados > 0 and user["id"] not in processed_users:
                    processed_users.add(user["id"])
                    try:
                        nome_user = bot.get_chat(user["id"]).first_name
                    except Exception:
                        nome_user = str(user['id'])
                    response.append({"nome": nome_user, "resgates": valores_resgatados})
        lista_ordenada = sorted(response, key=lambda x: -x["resgates"])[:10]
        return lista_ordenada
    def Servicos():
        data = _load_users_json_safe()
        ranking_atual = {}
        for user in data["users"]:
            for compra in user["compras"]:
                if compra["servico"] not in ranking_atual:
                    ranking_atual[compra["servico"]] = 0
                ranking_atual[compra['servico']] += 1
        servicos_ordenados = sorted(ranking_atual.items(), key=lambda x: -x[1])[:10]
        return servicos_ordenados

class Alertas():
    def adicionar_alerta(id, servico):
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if str(user["id"]) == str(id):
                    user["alertas"].append(servico)
                    _save_users_json_safe(data)
                    break
    def verificar_alerta(id, servico):
        data = _load_users_json_safe()
        for user in data["users"]:
            if str(user["id"]) == str(id):
                if str(servico) in user["alertas"]:
                    return True
                else:
                    return False
            pass
        return False
    def remover_alerta(id, servico):
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if str(user["id"]) == str(id):
                    user["alertas"].remove(servico)
                    _save_users_json_safe(data)
                    break
                pass
    def usuarios_para_receber_alerta(servico):
        data = _load_users_json_safe()
        destinos = []
        for user in data['users']:
            if servico in user["alertas"]:
                destinos.append(user["id"])
                continue
            pass
        return destinos
    def users_com_alertas():
        data = _load_users_json_safe()
        dados = []
        for user in data["users"]:
            for alerta in user["alertas"]:
                dados.append({"id": user["id"], "servico": alerta})
                continue
            pass
        return dados

class CronSaldoApi():
    def saldo_atual():
        data = _ensure_sms_provider_migration()
        provider_config = str(data.get("sms_provider", "herosms")).strip().lower()

        try:
            with open('settings/credenciais.json', 'r') as f:
                creds = json.load(f)
            api_key = creds.get('api_awesomeapi', '')

            url = "https://economia.awesomeapi.com.br/last/USD-BRL"
            if api_key:
                url += f"?apiKey={api_key}"

            response = requests.get(url, timeout=5)
            data_api = response.json()

            if "USDBRL" in data_api and "high" in data_api["USDBRL"]:
                valor_dolar = f'{float(data_api["USDBRL"]["high"]):.3f}'
            elif "USDBRL" in data_api and "bid" in data_api["USDBRL"]:
                valor_dolar = f'{float(data_api["USDBRL"]["bid"]):.3f}'
            else:
                valor_dolar = "5.70"

        except Exception as e:
            valor_dolar = "5.20"

        if provider_config == "todos":
            clients = sms_clients_all()
            total_balance_rublo = 0
            balances_info = []

            for client in clients:
                try:
                    balance = client.getBalance()["balance"]
                    balance_float = float(balance)
                    total_balance_rublo += balance_float
                    balance_real = balance_float * float(valor_dolar)
                    balance_dolar = balance_float
                    balances_info.append({
                        "provedor": client.provider,
                        "balance-dolar": f'{balance_dolar:.2f}',
                        "balance-real": f'{balance_real:.2f}'
                    })
                except Exception as e:
                    print(f"Erro ao obter saldo do {client.provider}: {e}")
                    balances_info.append({
                        "provedor": client.provider,
                        "balance-dolar": "0.00",
                        "balance-real": "0.00"
                    })

            total_balance_real = total_balance_rublo * float(valor_dolar)
            total_balance_dolar = total_balance_rublo
            return {
                "balance-dolar": f'{total_balance_dolar:.2f}',
                "balance-real": f'{total_balance_real:.2f}',
                "provedores": balances_info,
                "modo": "todos"
            }
        else:
            balance_rublo = sms.getBalance()["balance"]
            balance_real = float(balance_rublo) * float(valor_dolar)
            balance_dolar = float(balance_rublo)
            return {"balance-dolar": f'{balance_dolar:.2f}', "balance-real": f'{balance_real:.2f}'} 
    def saldo_minimo():
        with open('settings/cron_saldo_api.json', 'r') as f:
            data = json.load(f)
        return data["balance"]
    def mudar_saldo_minimo(min):
        with open('settings/cron_saldo_api.json', 'r') as f:
            data = json.load(f)
        data["balance"] = int(min)
        with open('settings/cron_saldo_api.json', 'w') as f:
            json.dump(data, f, indent=4)
    def status_aviso():
        with open('settings/cron_saldo_api.json', 'r') as f:
            data = json.load(f)
        return data["stats"]
    def mudar_status_aviso():
        with open('settings/cron_saldo_api.json', 'r') as f:
            data = json.load(f)
        if data["stats"] == True:
            data["stats"] = False
        elif data["stats"] == False:
            data["stats"] = True
        with open('settings/cron_saldo_api.json', 'w') as f:
            json.dump(data, f, indent=4)
    def destino_id():
        with open('settings/cron_saldo_api.json', 'r') as f:
            data = json.load(f)
        return data["to"]
    def mudar_destino_id(id):
        with open('settings/cron_saldo_api.json', 'r') as f:
            data = json.load(f)
        data["to"] = str(id)
        with open('settings/cron_saldo_api.json', 'w') as f:
            json.dump(data, f, indent=4)
    def tempo_aviso():
        with open('settings/cron_saldo_api.json', 'r') as f:
            data = json.load(f)
        return data["warn-time"]
    def mudar_tempo_aviso(time):
        with open('settings/cron_saldo_api.json', 'r') as f:
            data = json.load(f)
        data["warn-time"] = int(time)
        with open('settings/cron_saldo_api.json', 'w') as f:
            json.dump(data, f, indent=4)

class InfoUser():
    @staticmethod
    def _escrever_users_json(data):
        with open('database/users.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def _ler_users_json():
        import time
        max_tentativas = 5
        for tentativa in range(max_tentativas):
            try:
                if not os.path.exists('database/users.json'):
                    print(f"❌ Arquivo users.json não encontrado!")
                    return None
                
                file_size = os.path.getsize('database/users.json')
                if file_size == 0:
                    print(f"⚠️ Arquivo users.json está vazio! (tentativa {tentativa + 1})")
                    if tentativa < max_tentativas - 1:
                        time.sleep(0.2)
                        continue
                    return None
                
                with _users_json_lock:
                    with open('database/users.json', 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            print(f"⚠️ Conteúdo vazio após strip! (tentativa {tentativa + 1})")
                            if tentativa < max_tentativas - 1:
                                time.sleep(0.2)
                                continue
                            return None
                        
                        try:
                            data = json.loads(content)
                            return data
                        except json.JSONDecodeError as json_err:
                            print(f"❌ Erro JSON na tentativa {tentativa + 1}: {json_err}")
                            try:
                                import shutil
                                from datetime import datetime
                                backup_name = f'database/users.json.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
                                shutil.copy2('database/users.json', backup_name)
                                print(f"💾 Backup criado: {backup_name}")
                            except:
                                pass
                            if tentativa < max_tentativas - 1:
                                time.sleep(0.3)
                                continue
                            print("⚠️ Retornando estrutura JSON vazia devido a erro de parsing")
                            return {"users": []}
                        
            except FileNotFoundError:
                print(f"❌ Arquivo users.json não encontrado! (tentativa {tentativa + 1})")
                if tentativa < max_tentativas - 1:
                    time.sleep(0.2)
                    continue
                return None
            except PermissionError:
                print(f"❌ Sem permissão para ler users.json! (tentativa {tentativa + 1})")
                if tentativa < max_tentativas - 1:
                    time.sleep(0.3)
                    continue
                return None
            except Exception as e:
                print(f"❌ Erro inesperado ao ler users.json (tentativa {tentativa + 1}): {e}")
                if tentativa < max_tentativas - 1:
                    time.sleep(0.2)
                    continue
                return None
        return None
    
    def verificar_usuario(id):
        data = InfoUser._ler_users_json()
        if not data:
            return False
        try:
            for user in data["users"]:
                if int(user["id"]) == int(id):
                    return True
        except Exception as e:
            print(f"❌ Erro ao verificar usuário: {e}")
        return False
    def pix_gerados(id):
        data = _load_users_json_safe()
        for user in data["users"]:
            if str(user["id"]) == str(id):
                return int(user["pix_gerados"])
    def adicionar_pix_gerados(id):
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if str(user["id"]) == str(id):
                    user["pix_gerados"] += 1
                    _save_users_json_safe(data)
    def remover_pix_gerados(id):
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if str(user["id"]) == str(id):
                    user["pix_gerados"] -= 1
                    _save_users_json_safe(data)

    def _normalizar_favoritos(user):
        favoritos = user.get("favoritos", [])
        if not isinstance(favoritos, list):
            favoritos = []
        favoritos = [str(f) for f in favoritos]
        user["favoritos"] = favoritos
        return favoritos

    def favoritos(id):
        data = _load_users_json_safe()
        for user in data.get("users", []):
            if int(user.get("id", 0)) == int(id):
                return InfoUser._normalizar_favoritos(user)
        return []

    def is_favorito(id, servico_id):
        favoritos = InfoUser.favoritos(id)
        return str(servico_id) in favoritos

    def toggle_favorito(id, servico_id):
        servico_id = str(servico_id)
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data.get("users", []):
                if int(user.get("id", 0)) == int(id):
                    favoritos = InfoUser._normalizar_favoritos(user)
                    if servico_id in favoritos:
                        favoritos.remove(servico_id)
                        _save_users_json_safe(data)
                        return False
                    favoritos.append(servico_id)
                    _save_users_json_safe(data)
                    return True
        return False
    
    def eh_constante(user_id, min_compras=10):
        try:
            data = _load_users_json_safe()
            for user in data.get("users", []):
                if int(user.get("id")) == int(user_id):
                    compras = len(user.get("historico", []))
                    return compras >= min_compras
            return False
        except Exception:
            return False
    
    def salvar_qr_message_id(user_id, message_id):
        try:
            with _users_json_lock:
                data = _load_users_json_safe()
                
                for user in data["users"]:
                    if str(user["id"]) == str(user_id):
                        if 'qr_messages' not in user:
                            user['qr_messages'] = []
                        user['qr_messages'].append(message_id)
                        break
                
                _save_users_json_safe(data)
                    
        except Exception as e:
            print(f"Erro ao salvar ID da mensagem QR: {e}")
    def novo_afiliado(usuario, indicador):
        print(f"[NOVO_AFILIADO] Iniciando registro de indicação")
        print(f"[NOVO_AFILIADO] Usuário (indicado): {usuario}")
        print(f"[NOVO_AFILIADO] Indicador: {indicador}")
        
        with _users_json_lock:
            data = _load_users_json_safe()
            
            usuario_encontrado = False
            for user in data["users"]:
                if int(user["id"]) == int(usuario):
                    usuario_encontrado = True
                    print(f"[NOVO_AFILIADO] Usuário {usuario} encontrado no banco")
                    
                    if user["afiliado_por"] != 0:
                        print(f"[NOVO_AFILIADO] ⚠️ Usuário {usuario} já tem um indicador: {user['afiliado_por']}")
                        return
                    
                    user["afiliado_por"] = int(indicador)
                    print(f"[NOVO_AFILIADO] ✅ Campo 'afiliado_por' atualizado para {indicador}")
                    break
            
            if not usuario_encontrado:
                print(f"[NOVO_AFILIADO] ❌ Usuário {usuario} NÃO encontrado no banco!")
                return
            
            indicador_encontrado = False
            for user in data["users"]:
                if int(user["id"]) == int(indicador):
                    indicador_encontrado = True
                    print(f"[NOVO_AFILIADO] Indicador {indicador} encontrado no banco")
                    
                    if int(usuario) in user["afiliados"]:
                        print(f"[NOVO_AFILIADO] ⚠️ Usuário {usuario} já está na lista de afiliados")
                        return
                    
                    user["afiliacoes"] += 1
                    user["afiliados"].append({"id_afiliado": int(usuario)})
                    print(f"[NOVO_AFILIADO] ✅ Usuário {usuario} adicionado à lista de afiliados")
                    print(f"[NOVO_AFILIADO] ✅ Contador de afiliações incrementado para {user['afiliacoes']}")
                    break
            
            if not indicador_encontrado:
                print(f"[NOVO_AFILIADO] ❌ Indicador {indicador} NÃO encontrado no banco!")
                return
            
            _save_users_json_safe(data)
            
            print(f"[NOVO_AFILIADO] ✅ Indicação registrada com sucesso no banco de dados!")
            return
    def pegar_pais_atual(id):
        data = InfoUser._ler_users_json()
        if not data:
            return False
        try:
            for user in data["users"]:
                if int(user["id"]) == int(id):
                    return user["pais-atual"]
        except Exception as e:
            print(f"❌ Erro ao pegar país atual: {e}")
        return False
    def mudar_pais_atual(id, pais):
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if int(user["id"]) == int(id):
                    user["pais-atual"] = pais
                    _save_users_json_safe(data)
                    return True
                pass
            return False
    def novo_usuario(id):
        from datetime import datetime
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if str(id) == str(user["id"]):
                    return
                pass
            data["users"].append({
                "id": int(id), 
                "banned": "False", 
                "afiliado_por": 0, 
                "saldo": 0, 
                "gift_redeemed": [], 
                "total_compras": 0, 
                "compras": [], 
                "total_pagos": 0, 
                "pagamentos": [], 
                "pontos_indicado": 0, 
                "afiliacoes": 0, 
                "afiliados": [], 
                "pais-atual": '73', 
                "alertas": [], 
                "pix_gerados": 0,
                    "data_registro": datetime.now().isoformat(),
                    "favoritos": []
            })
            _save_users_json_safe(data)
    def pegar_afiliado(id):
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        for user in data["users"]:
            if int(user["id"]) == int(id):
                return user["afiliado_por"]
            else:
                pass
        return False
    def verificar_ban(id):
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        for user in data["users"]:
            if int(user["id"]) == int(id):
                if user["banned"] == 'True':
                    return True
                else:
                    return False
            pass
    def dar_ban(id):
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if int(user["id"]) == int(id):
                    user["banned"] = "True"
                    break
                pass
            _save_users_json_safe(data)
    def tirar_ban(id):
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if int(user["id"]) == int(id):
                    user["banned"] = "False"
                    break
                pass
            _save_users_json_safe(data)
    def saldo(id):
        data = _load_users_json_safe()
        for user in data["users"]:
            if int(user["id"]) == int(id):
                return float(user["saldo"])
    def add_saldo(id, novo_saldo):
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if int(user["id"]) == int(id):
                    user["saldo"] += float(novo_saldo)
                    break
                pass
            _save_users_json_safe(data)
    
    def verificar_reembolso_duplicado(user_id, activation_id):
        data = _load_users_json_safe()
        
        for user in data["users"]:
            if int(user["id"]) == int(user_id):
                if "reembolsos_processados" not in user:
                    user["reembolsos_processados"] = []
                
                return str(activation_id) in user["reembolsos_processados"]
        
        return False
    
    def marcar_como_reembolsado(user_id, activation_id):
        with _users_json_lock:
            data = _load_users_json_safe()
            
            for user in data["users"]:
                if int(user["id"]) == int(user_id):
                    if "reembolsos_processados" not in user:
                        user["reembolsos_processados"] = []
                    
                    if str(activation_id) not in user["reembolsos_processados"]:
                        user["reembolsos_processados"].append(str(activation_id))
                    
                    for compra in user.get("compras", []):
                        if str(compra.get("id_ativacao")) == str(activation_id):
                            compra["status"] = "reembolsada"
                            print(f"✅ [STATUS COMPRA] ID:{activation_id} | User:{user_id} | Status atualizado para: reembolsada")
                            break
                    
                    break
            
            _save_users_json_safe(data)
    
    def marcar_compra_como_concluida(user_id, activation_id):
        with _users_json_lock:
            data = _load_users_json_safe()
            
            for user in data["users"]:
                if int(user["id"]) == int(user_id):
                    for compra in user.get("compras", []):
                        if str(compra.get("id_ativacao")) == str(activation_id):
                            compra["status"] = "concluida"
                            print(f"✅ [STATUS COMPRA] ID:{activation_id} | User:{user_id} | Status atualizado para: concluida")
                            break
                    break
            
            _save_users_json_safe(data)
    def tirar_saldo(id, novo_saldo):
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if int(user["id"]) == int(id):
                    user["saldo"] -= float(novo_saldo)
                    _save_users_json_safe(data)
                    break
                pass
            False
    def mudar_saldo(id, novo_saldo):
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if int(user["id"]) == int(id):
                    user["saldo"] = float(novo_saldo)
                    break
                pass
            _save_users_json_safe(data)
    def gifts_resgatados(id):
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        for user in data["users"]:
            if int(user["id"]) == int(id):
                total = 0
                for gift in user["gift_redeemed"]:
                    total += float(gift["valor"])
                return float(total)
            pass
        return 0
    def total_compras(id):
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        for user in data["users"]:
            if int(user["id"]) == int(id):
                return user["total_compras"]
            pass
    def total_pagos(id):
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        for user in data["users"]:
            if int(user["id"]) == int(id):
                return user["total_pagos"]
            pass
        return False
    def pix_inseridos(id):
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        quantity = 0.0
        for user in data["users"]:
            if int(user["id"]) == int(id):
                if len(user["pagamentos"]) > 0:
                    for pagamento in user["pagamentos"]:
                        quantity += float(pagamento["valor"])
                    pass
                pass
            pass
        return float(quantity)
    def pontos_indicacao(id):
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        for user in data["users"]:
            if int(user["id"]) == int(id):
                return user["pontos_indicado"]
            pass
    def trocar_pontos(id):
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if int(user["id"]) == int(id):
                    if int(user["pontos_indicado"]) >= int(AfiliadosInfo.minimo_pontos_pra_saldo()):
                        somar = int(user["pontos_indicado"]) * AfiliadosInfo.multiplicador_pontos()
                        user["pontos_indicado"] = 0
                        user["saldo"] = float(somar)
                        _save_users_json_safe(data)
                        return True
                    else:
                        return False
                pass
    def quantidade_afiliados(id):
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        for user in data["users"]:
            if int(user["id"]) == int(id):
                return int(user["afiliacoes"])
        return None
    
    def quantidade_afiliados_com_recarga(id):
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        
        indicador = None
        for user in data["users"]:
            if int(user["id"]) == int(id):
                indicador = user
                break
        
        if not indicador:
            return 0
        
        indicados_com_recarga = 0
        for afiliado_info in indicador.get("afiliados", []):
            id_afiliado = afiliado_info.get("id_afiliado")
            
            for user in data["users"]:
                if int(user["id"]) == int(id_afiliado):
                    if len(user.get("pagamentos", [])) > 0:
                        indicados_com_recarga += 1
                    break
        
        return indicados_com_recarga
    
    def valor_total_ganho_indicacoes(id):
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        
        for user in data["users"]:
            if int(user["id"]) == int(id):
                pontos_indicacao = float(user.get("pontos_indicacao", 0))
                saldo_indicacao = float(user.get("saldo_indicacao", 0))
                return pontos_indicacao + saldo_indicacao
        
        return 0.0
    
    def pegar_afiliado_por(id):
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        for user in data["users"]:
            if int(user["id"]) == int(id):
                return int(user.get("afiliado_por", 0))
        return 0
    
    def verificar_acessos_ativos(id):
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        ativacoes_disponiveis = []
        for user in data["users"]:
            if str(user["id"]) == str(id):
                for compra in user["compras"]:
                    id_atv = compra["id_ativacao"]
                    response = InfoApi.pegar_status_numero(str(id_atv))
                    if response != None:
                        if response != False:
                            if response.startswith('Aguardan'):
                                ativacoes_disponiveis.append(compra)
        return ativacoes_disponiveis
    
    def total_usuarios():
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        return len(data["users"])
    
    def usuarios_ultimos_dias(dias):
        from datetime import datetime, timedelta
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        
        data_limite = datetime.now() - timedelta(days=dias)
        usuarios_novos = 0
        
        for user in data["users"]:
            if 'data_registro' in user:
                try:
                    data_registro = datetime.fromisoformat(user['data_registro'])
                    if data_registro >= data_limite:
                        usuarios_novos += 1
                except:
                    pass
        
        return usuarios_novos
    
    def usuarios_por_mes(mes, ano):
        from datetime import datetime
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        
        usuarios_mes = 0
        
        for user in data["users"]:
            if 'data_registro' in user:
                try:
                    data_registro = datetime.fromisoformat(user['data_registro'])
                    if data_registro.month == mes and data_registro.year == ano:
                        usuarios_mes += 1
                except:
                    pass
        
        return usuarios_mes
    
    def usuarios_banidos():
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        
        usuarios_banidos = 0
        for user in data["users"]:
            if user["banned"] == 'True':
                usuarios_banidos += 1
        
        return usuarios_banidos
    
    def total_afiliados():
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        
        total_afiliados = 0
        for user in data["users"]:
            if user["afiliacoes"] > 0:
                total_afiliados += 1
        
        return total_afiliados
    
    def total_compras_geral():
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        
        total_compras = 0
        for user in data["users"]:
            total_compras += user["total_compras"]
        
        return total_compras
    
    def total_pagamentos_geral():
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        
        total_pagamentos = 0
        for user in data["users"]:
            total_pagamentos += user["total_pagos"]
        
        return total_pagamentos
    
    def valor_total_pagamentos():
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        
        valor_total = 0
        for user in data["users"]:
            for pagamento in user["pagamentos"]:
                valor_total += float(pagamento["valor"])
        
        return valor_total
    
    def adicionar_data_registro_usuarios_existentes():
        from datetime import datetime
        with _users_json_lock:
            data = _load_users_json_safe()
            
            modificado = False
            for user in data["users"]:
                if "data_registro" not in user:
                    user["data_registro"] = datetime.now().isoformat()
                    modificado = True
            
            if modificado:
                _save_users_json_safe(data)
                return True
            return False

class MudancaHistorico():
    def mudar_gift_resgatado(id, valor):
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if int(user["id"]) == int(id):
                    user["gift_redeemed"].append({"valor": float(valor), "data": f"{ViewTime.data_atual()} as {ViewTime.hora_atual()}"})
                    _save_users_json_safe(data)
                    break
                pass
    
    def add_reembolso(user_id, id_ativacao, valor):
        """
        Registra um reembolso no histórico do usuário
        """
        with _users_json_lock:
            data = _load_users_json_safe()
            
            for user in data["users"]:
                if int(user["id"]) == int(user_id):
                    if "reembolsos_historico" not in user:
                        user["reembolsos_historico"] = []
                    
                    user["reembolsos_historico"].append({
                        "id_ativacao": id_ativacao,
                        "valor": float(valor),
                        "data": f"{ViewTime.data_atual()} as {ViewTime.hora_atual()}",
                        "timestamp": time.time(),
                        "motivo": "timeout_automatico"
                    })
                    
                    # Também pode registrar no histórico geral se existir
                    if "historico" not in user:
                        user["historico"] = []
                    
                    user["historico"].append({
                        "tipo": "reembolso",
                        "id_ativacao": id_ativacao,
                        "valor": float(valor),
                        "data": f"{ViewTime.data_atual()} as {ViewTime.hora_atual()}",
                        "timestamp": time.time(),
                        "motivo": "timeout_automatico"
                    })
                    break
            
            _save_users_json_safe(data)
            print(f"✅ [HISTÓRICO] Reembolso registrado para usuário {user_id}, ativação {id_ativacao}")
            return True
    
    def add_compra(id, servico_id, valor, numero, servico, id_ativacao, provedor=None, message_id=None):
        import time
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if int(id) == int(user["id"]):
                    user["total_compras"] +=1
                    timestamp_recebimento = time.time()
                    compra_data = {
                        "id-servico": servico_id,
                        "valor": valor,
                        "numero": numero,
                        "servico": servico,
                        "id_ativacao": id_ativacao,
                        "provedor": provedor,
                        "data": f"{ViewTime.data_atual()} as {ViewTime.hora_atual()}",
                        "timestamp_recebimento": timestamp_recebimento,
                        "status": "ativa"
                    }
                    if message_id:
                        compra_data["message_id"] = message_id
                    user["compras"].append(compra_data)
                    break
                pass
            _save_users_json_safe(data)
    
    def update_message_id_ultima_compra(id, message_id):
        import time
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if int(id) == int(user["id"]):
                    if user["compras"]:
                        user["compras"][-1]["message_id"] = message_id
                    break
                pass
            _save_users_json_safe(data)
    
    def add_pagamentos(id, valor, id_pag, valor_indicacao):
        with _users_json_lock:
            data = _load_users_json_safe()
            afiliado_por = 0
            for user in data["users"]:
                if int(user["id"]) == int(id):
                    payment_exists = any(p.get("id_pagamento") == id_pag for p in user.get("pagamentos", []))
                    if payment_exists:
                        print(f"⚠️ [PAGAMENTO DUPLICADO] ID {id_pag} já existe para usuário {id}, ignorando...")
                        return
                    
                    afiliado_por = user["afiliado_por"]
                    user["total_pagos"] += 1
                    user["pagamentos"].append({
                        "id_pagamento": id_pag, 
                        "valor": valor, 
                        "data": f"{ViewTime.data_atual()} as {ViewTime.hora_atual()}"
                    })
                    break
                pass
            
            if AfiliadosInfo.status_afiliado() == True and int(afiliado_por) != 0:
                for user in data["users"]:
                    if int(afiliado_por) == int(user["id"]):
                        user["pontos_indicado"] += float(valor_indicacao)
                        user["saldo"] += float(valor_indicacao)
                        break
                    pass
            
            _save_users_json_safe(data)
    
    def zerar_pontos(id):
        with _users_json_lock:
            data = _load_users_json_safe()
            for user in data["users"]:
                if int(user["id"]) == int(id):
                    user["pontos_indicado"] = 0
                    _save_users_json_safe(data)
                    break
                else:
                    pass
    
    def add_pagamentos_zucpay(id, valor, id_pag, valor_indicacao):
        print(f"🔍 DEBUG: Tentando salvar pagamento Zucpay")
        print(f"🔍 DEBUG: ID usuário: {id}, Valor: {valor}, ID pagamento: {id_pag}")
        
        with _users_json_lock:
            data = _load_users_json_safe()
            
            user_found = False
            afiliado_por = 0
            for user in data["users"]:
                if int(user["id"]) == int(id):
                    print(f"✅ DEBUG: Usuário {id} encontrado!")
                    
                    payment_exists = any(p.get("id_pagamento") == id_pag for p in user.get("pagamentos", []))
                    if payment_exists:
                        print(f"⚠️ [PAGAMENTO DUPLICADO] ID {id_pag} já existe para usuário {id}, ignorando...")
                        return False
                    
                    afiliado_por = user["afiliado_por"]
                    user["total_pagos"] += 1
                    payment_data = {
                        "id_pagamento": id_pag, 
                        "valor": valor, 
                        "data": f"{ViewTime.data_atual()} as {ViewTime.hora_atual()}",
                        "status": "pending",
                        "plataforma": "zucpay",
                        "created_at": datetime.now().isoformat()
                    }
                    user["pagamentos"].append(payment_data)
                    print(f"✅ DEBUG: Pagamento adicionado: {payment_data}")
                    user_found = True
                    break
                pass
            
            if not user_found:
                print(f"❌ DEBUG: Usuário {id} NÃO encontrado!")
                return False
            
            if AfiliadosInfo.status_afiliado() == True and int(afiliado_por) != 0:
                for user in data["users"]:
                    if int(afiliado_por) == int(user["id"]):
                        user["pontos_indicado"] += float(valor_indicacao)
                        user["saldo"] += float(valor_indicacao)
                        break
                    pass
            
            _save_users_json_safe(data)
            print(f"✅ DEBUG: Arquivo salvo com sucesso!")
            return True

class GiftCard():
    def validar_gift(codigo):
        with open("database/gift_card.json", 'r') as f:
            data = json.load(f)
        for gift in data['gift']:
            if gift["codigo"] == codigo:
                valor = float(gift["valor"])
                return True, valor
        return False, 0
    def listar_gift():
        with open('database/gift_card.json', 'r') as f:
            data = json.load(f)
        msg = ''
        for gift in data["gift"]:
            msg += f'<code>{gift["codigo"]}</code> R${float(gift["valor"]):.2f}\n'
        return msg
    def create_gift(codigo, valor):
        with open("database/gift_card.json", 'r') as f:
            data = json.load(f)
        data["gift"].append({"codigo": codigo, "valor": float(valor)})
        with open("database/gift_card.json", 'w') as j:
            json.dump(data, j, indent=4)
        return True
    def del_gift(codigo):
        with open("database/gift_card.json", 'r') as f:
            data = json.load(f)
        for gift in data["gift"]:
            if gift["codigo"] == codigo:
                data["gift"].remove(gift)
                with open("database/gift_card.json", 'w') as f:
                    json.dump(data, f, indent=4)
                return True
            pass
        return False

class FuncaoTransmitir():
    def pegar_foto():
        with open('database/info_transmitir.json', 'r') as f:
            data = json.load(f)
            return data["photo"]
    def pegar_texto():
        with open('database/info_transmitir.json', 'r') as f:
            data = json.load(f)
            return data["texto"]
    def pegar_markup():
        with open('database/info_transmitir.json', 'r') as f:
            data = json.load(f)
            return data["markup"]
    def adicionar_foto(photo):
        with open('database/info_transmitir.json', 'r') as f:
            data = json.load(f)
        data["photo"] = photo
        with open('database/info_transmitir.json', 'w') as f:
            data = json.dump(data, f, indent=4)
    def adicionar_texto(txt):
        with open('database/info_transmitir.json', 'r') as f:
            data = json.load(f)
        data["texto"] = txt
        with open('database/info_transmitir.json', 'w') as f:
            json.dump(data, f, indent=4)
    def adicionar_markup(markup):
        with open('database/info_transmitir.json', 'r') as f:
            data = json.load(f)
        if markup is not None:
            inline_keyboard = []
            for row in markup.keyboard:
                row_buttons = []
                for but in row:
                    button_dict = {
                        'text': but.text,
                        'url': but.url
                    }
                    row_buttons.append(button_dict)
                inline_keyboard.append(row_buttons)
            data["markup"] = inline_keyboard
        else:
            data["markup"] = None
        with open('database/info_transmitir.json', 'w') as f:
            json.dump(data, f, indent=4)
    def zerar_infos():
        with open('database/info_transmitir.json', 'r') as f:
            data = json.load(f)
        data["texto"] = None
        data["photo"] = None
        data["markup"] = None
        with open('database/info_transmitir.json', 'w') as f:
            json.dump(data, f, indent=4)

class Admin():
    def total_users():
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        q = 0
        for i in data["users"]:
            q += 1
        return q
    def verificar_admin(id):
        with open('database/admins.json', 'r') as f:
            data = json.load(f)
        for admin in data["admins"]:
            if int(admin["id"]) == int(id):
                return True
            pass
        return False
    def add_admin(id):
        with open('database/admins.json', 'r') as f:
            data = json.load(f)
        data["admins"].append({"id": int(id)})
        with open('database/admins.json', 'w') as f:
            json.dump(data, f, indent=4)
        return True
    def quantidade_admin():
        with open('database/admins.json', 'r') as f:
            data = json.load(f)
        quantity = 0
        for admin in data["admins"]:
            quantity +=1
        return quantity
    def listar_admins():
        with open('database/admins.json', 'r') as f:
            data = json.load(f)
        adm_list = '<b>👮 LISTA DE ADMINS:</b> 🚨\n\n'
        for admin in data["admins"]:
            adm_list += f'\n<b>ADMIN ID</b>: <code>{admin["id"]}</code>'
        return adm_list
    def remover_admin(id):
        with open('database/admins.json', 'r') as f:
            data = json.load(f)
        for admin in data["admins"]:
            if int(admin["id"]) == int(id):
                data["admins"].remove(admin)
                with open('database/admins.json', 'w') as f:
                    json.dump(data, f, indent=4)
                return True
            pass

class Textos():
    def start(message):
        first_name = message.chat.first_name
        username = message.chat.username
        id = message.chat.id
        if str(message.chat.id).startswith('-'):
            id = message.from_user.id
            first_name = message.from_user.first_name
            username = message.from_user.username
        link_afiliado = f'https://t.me/{CredentialsChange.user_bot()}?start={message.chat.id}'
        saldo = InfoUser.saldo(id)
        pontos_indicacao = InfoUser.pontos_indicacao(id)
        quantidade_afiliados = InfoUser.quantidade_afiliados(id)
        quantidade_compras = InfoUser.total_compras(id)
        pix_inseridos = f'{InfoUser.pix_inseridos(id):.2f}'
        gifts_resgatados = f'{InfoUser.gifts_resgatados(id):.2f}'
        pais_id = InfoUser.pegar_pais_atual(message.chat.id)
        pais_nome = InfoApi.pegar_pais(pais_id)
        
        with open('database/users.json', 'r') as f:
            data = json.load(f)
        
        saldo_recarregado = 0.0
        saldo_recebido = 0.0
        saldo_gift = 0.0
        bonus_recarga = 0.0
        bonus_referencia = 0.0
        
        for user in data["users"]:
            if int(user["id"]) == int(id):
                for pagamento in user.get("pagamentos", []):
                    if pagamento.get("status") == "approved":
                        saldo_recarregado += float(pagamento.get("valor", 0))
                
                for gift in user.get("gift_redeemed", []):
                    saldo_gift += float(gift.get("valor", 0))
                
                bonus_referencia = float(user.get("pontos_indicado", 0))
                
                saldo_total = float(user.get("saldo", 0))
                saldo_calculado = saldo_recarregado + saldo_gift + bonus_referencia
                
                diferenca = saldo_total - saldo_calculado
                if diferenca > 0:
                    bonus_recarga = diferenca
                else:
                    bonus_recarga = 0.0
                
                saldo_recebido = 0.0
                
                break
        
        with open('textos/start.txt', 'r', encoding='utf-8') as f:
            texto = f.read()
        
        texto = texto.replace('{first_name}', f'{first_name}').replace('{username}', f'@{username}').replace('{id}', f'{id}').replace('{link_afiliado}', f'{link_afiliado}').replace('{saldo}', f'{saldo:.2f}').replace('{pontos_indicacao}', f'{pontos_indicacao}').replace('{quantidade_afiliados}', f'{quantidade_afiliados}').replace('{quantidade_compras}', f'{quantidade_compras}').replace('{pix_inseridos}', f'{pix_inseridos}').replace('{gifts_resgatados}', f'{gifts_resgatados}').replace('{pais}', f'{pais_id}').replace('{pais_nome}', f'{pais_nome}').replace('{saldo_recarregado}', f'{saldo_recarregado:.2f}').replace('{saldo_recebido}', f'{saldo_recebido:.2f}').replace('{saldo_gift}', f'{saldo_gift:.2f}').replace('{bonus_recarga}', f'{bonus_recarga:.2f}').replace('{bonus_referencia}', f'{bonus_referencia:.2f}')
        
        return texto
    def perfil(message):
        first_name = message.chat.first_name
        username = message.chat.username
        id = message.chat.id
        link_afiliado = f'https://t.me/{CredentialsChange.user_bot()}?start={message.chat.id}'
        saldo = InfoUser.saldo(id)
        pontos_indicacao = InfoUser.pontos_indicacao(id)
        quantidade_afiliados = InfoUser.quantidade_afiliados(id)
        quantidade_compras = InfoUser.total_compras(id)
        pix_inseridos = f'{InfoUser.pix_inseridos(id):.2f}'
        gifts_resgatados = f'{InfoUser.gifts_resgatados(id):.2f}'
        with open('textos/perfil.txt', 'r', encoding='utf-8') as f:
            texto = f.read()
        texto = texto.replace('{first_name}', f'{first_name}').replace('{username}', f'@{username}').replace('{id}', f'{id}').replace('{link_afiliado}', f'{link_afiliado}').replace('{saldo}', f'{saldo:.2f}').replace('{pontos_indicacao}', f'{pontos_indicacao}').replace('{quantidade_afiliados}', f'{quantidade_afiliados}').replace('{quantidade_compras}', f'{quantidade_compras}').replace('{pix_inseridos}', f'{pix_inseridos}').replace('{gifts_resgatados}', f'{gifts_resgatados}')
        return texto
    def adicionar_saldo(message):
        first_name = message.chat.first_name
        username = message.chat.username
        id = message.chat.id
        link_afiliado = f'https://t.me/{CredentialsChange.user_bot()}?start={message.chat.id}'
        saldo = InfoUser.saldo(id)
        pontos_indicacao = InfoUser.pontos_indicacao(id)
        quantidade_afiliados = InfoUser.quantidade_afiliados(id)
        quantidade_compras = InfoUser.total_compras(id)
        pix_inseridos = f'{InfoUser.pix_inseridos(id):.2f}'
        gifts_resgatados = f'{InfoUser.gifts_resgatados(id):.2f}'
        with open('textos/adicionar_saldo.txt', 'r', encoding='utf-8') as f:
            texto = f.read()
        texto = texto.replace('{first_name}', f'{first_name}').replace('{username}', f'@{username}').replace('{id}', f'{id}').replace('{link_afiliado}', f'{link_afiliado}').replace('{saldo}', f'{saldo:.2f}').replace('{pontos_indicacao}', f'{pontos_indicacao}').replace('{quantidade_afiliados}', f'{quantidade_afiliados}').replace('{quantidade_compras}', f'{quantidade_compras}').replace('{pix_inseridos}', f'{pix_inseridos}').replace('{gifts_resgatados}', f'{gifts_resgatados}')
        return texto
    def pix_manual(message):
        first_name = message.chat.first_name
        username = message.chat.username
        id = message.chat.id
        saldo = InfoUser.saldo(id)
        deposito_minimo = f'{CredentialsChange.InfoPix.deposito_minimo_pix():.2f}'
        with open('textos/pix_manual.txt', 'r', encoding='utf-8') as f:
            texto = f.read()
        texto = texto.replace('{first_name}', f'{first_name}').replace('{username}', f'@{username}').replace('{id}', f'{id}').replace('{saldo}', f'{saldo:.2f}').replace('{deposito_minimo}', f'{deposito_minimo}')
        return texto
    def pix_automatico(message, pix_copia_cola, expiracao, id_pagamento, valor):
        first_name = message.chat.first_name
        username = message.chat.username
        id = message.chat.id
        saldo = InfoUser.saldo(id)
        deposito_minimo = f'{CredentialsChange.InfoPix.deposito_minimo_pix():.2f}'
        pix_inseridos = f'{InfoUser.pix_inseridos(id):.2f}'
        with open('textos/pix_automatico.txt', 'r', encoding='utf-8') as f:
            texto = f.read()
        texto = texto.replace('{first_name}', f'{first_name}').replace('{username}', f'@{username}').replace('{id}', f'{id}').replace('{saldo}', f'{saldo:.2f}').replace('{pix_inseridos}', f'{pix_inseridos}').replace('{pix_copia_cola}', f'{pix_copia_cola}').replace('{expiracao}', f'{expiracao}').replace('{id_pagamento}', f'{id_pagamento}').replace('{valor}', f'{valor}').replace('{deposito_minimo}', f'{deposito_minimo}')
        return texto
    def pagamento_expirado(message, id_pagamento, valor):
        first_name = message.chat.first_name
        username = message.chat.username
        id = message.chat.id
        link_afiliado = f'https://t.me/{CredentialsChange.user_bot()}?start={message.chat.id}'
        saldo = InfoUser.saldo(id)
        with open('textos/pagamento_expirado.txt', 'r', encoding='utf-8') as f:
            texto = f.read()
        texto = texto.replace('{first_name}', f'{first_name}').replace('{username}', f'@{username}').replace('{id}', f'{id}').replace('{link_afiliado}', f'{link_afiliado}').replace('{saldo}', f'{saldo:.2f}').replace('{id_pagamento}', f'{id_pagamento}').replace('{valor}', f'{valor}')
        return texto
    def pagamento_aprovado(message, id_pagamento, valor):
        first_name = message.chat.first_name
        username = message.chat.username
        id = message.chat.id
        link_afiliado = f'https://t.me/{CredentialsChange.user_bot()}?start={message.chat.id}'
        saldo = InfoUser.saldo(id)
        with open('textos/pagamento_aprovado.txt', 'r', encoding='utf-8') as f:
            texto = f.read()
        texto = texto.replace('{first_name}', f'{first_name}').replace('{username}', f'@{username}').replace('{id}', f'{id}').replace('{link_afiliado}', f'{link_afiliado}').replace('{saldo}', f'{saldo:.2f}').replace('{id_pagamento}', f'{id_pagamento}').replace('{valor}', f'{valor}')
        return texto
    def menu_comprar(message):
        first_name = message.chat.first_name
        username = message.chat.username
        id = message.chat.id
        link_afiliado = f'https://t.me/{CredentialsChange.user_bot()}?start={message.chat.id}'
        saldo = InfoUser.saldo(id)
        pontos_indicacao = InfoUser.pontos_indicacao(id)
        quantidade_afiliados = InfoUser.quantidade_afiliados(id)
        quantidade_compras = InfoUser.total_compras(id)
        pix_inseridos = InfoUser.pix_inseridos(id)
        gifts_resgatados = InfoUser.gifts_resgatados(id)
        with open('textos/menu_comprar.txt', 'r', encoding='utf-8') as f:
            texto = f.read()
        texto = texto.replace('{first_name}', f'{first_name}').replace('{username}', f'@{username}').replace('{id}', f'{id}').replace('{link_afiliado}', f'{link_afiliado}').replace('{saldo}', f'{saldo:.2f}').replace('{pontos_indicacao}', f'{pontos_indicacao}').replace('{quantidade_afiliados}', f'{quantidade_afiliados}').replace('{quantidade_compras}', f'{quantidade_compras}').replace('{pix_inseridos}', f'{pix_inseridos}').replace('{gifts_resgatados}', f'{gifts_resgatados}')
        return texto
    def exibir_servico(message, servico, valor, pais, count):
        saldo = InfoUser.saldo(message.chat.id)
        with open('textos/exibir_servico.txt', 'r', encoding='utf-8') as f:
            texto = f.read()
        with open('database/notas.json', 'r') as f:
            data = json.load(f)
        notas_disp = []
        for nota in data["nota"]:
            notas_disp.append(nota["texto"])
        if len(notas_disp) == 0:
            notas_disp = ['Esse bot não tem notas salvas.']
        nota = random.choice(notas_disp)
        texto = texto.replace('{servico}', f'{servico}').replace('{valor}', f'{float(valor):.2f}').replace('{pais}', f'{pais}').replace('{saldo}', f'{float(saldo):.2f}').replace('{count}', f'{count}').replace('{nota}', f'{nota}')
        return texto
    def mensagem_comprou(message, nome, numero, operadora, valor):
        if message.from_user.is_bot:
            saldo = InfoUser.saldo(message.chat.id)
        else:
            saldo = InfoUser.saldo(message.from_user.id)
        with open('textos/mensagem_comprou.txt', 'r', encoding='utf-8') as f:
            texto = f.read()
        texto = texto.replace('{nome}', f'{nome}').replace('{valor}', f'{valor}').replace('{saldo}', f'{float(saldo):.2f}').replace('{numero}', f'{numero}').replace('{operadora}', f'{operadora}').replace('\\n', '\n')
        return texto
    def termos(message):
        with open('textos/termos.txt', 'r', encoding='utf-8') as f:
            txt = f.read()
        return txt
    def ajuda(message):
        with open('textos/ajuda.txt', 'r', encoding='utf-8') as f:
            txt = f.read()
        link_suporte = CredentialsChange.SuporteInfo.link_suporte()
        txt = txt.replace('{link_suporte}', link_suporte)
        return txt
    def id(message):
        with open('textos/id.txt', 'r', encoding='utf-8') as f:
            d = f.read()
            d = d.replace('{id}', f'{message.chat.id}')
        return d
    def afiliados(message):
        with open('textos/afiliados.txt', 'r', encoding='utf-8') as f:
            d = f.read()
        
        ind = InfoUser.quantidade_afiliados(message.chat.id)
        per = AfiliadosInfo.porcentagem_por_indicacao()
        gan = f'{float(InfoUser.pontos_indicacao(message.chat.id)):.2f}'
        gan = str(gan).replace('.', ',')
        lin = f'https://t.me/{CredentialsChange.user_bot()}?start={message.chat.id}'
        
        ind_com_recarga = InfoUser.quantidade_afiliados_com_recarga(message.chat.id)
        valor_total_ganho = InfoUser.valor_total_ganho_indicacoes(message.chat.id)
        valor_total_ganho_formatado = f'{valor_total_ganho:.2f}'.replace('.', ',')
        
        texto = d.replace('{ind}', f'{ind}').replace('{per}', f'{per}').replace('{gan}', f'{gan}').replace('{lin}', f'{lin}').replace('{ind_recarga}', f'{ind_com_recarga}').replace('{valor_total}', f'{valor_total_ganho_formatado}')
        return texto
    def saldo(message):
        saldo = f'{float(InfoUser.saldo(message.chat.id)):.2f}'
        with open('textos/saldo.txt', 'r', encoding='utf-8') as f:
            d = f.read()
            d = d.replace('{saldo}', f'{saldo}')
        return d
    
    def verificacao_canal(message, link_canal):
        try:
            with open('textos/verificacao_canal.txt', 'r', encoding='utf-8') as f:
                texto = f.read()
            return texto.format(link_canal=link_canal)
        except FileNotFoundError:
            return f'🔗 <b>VERIFICAÇÃO DE CANAL OBRIGATÓRIA</b>\n\n⚠️ Para usar este bot, você precisa entrar no nosso canal oficial primeiro.\n\n📢 <b>Canal:</b> {link_canal}\n\n✅ Após entrar no canal, clique no botão "✅ JÁ ENTREI NO CANAL" abaixo.'

class MudarTexto():
    def start(texto):
        with open('textos/start.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def perfil(texto):
        with open('textos/perfil.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def adicionar_saldo(texto):
        with open('textos/adicionar_saldo.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def pix_manual(texto):
        with open('textos/pix_manual.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def pix_automatico(texto):
        with open('textos/pix_automatico.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def pagamento_expirado(texto):
        with open('textos/pagamento_expirado.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def pagamento_aprovado(texto):
        with open('textos/pagamento_aprovado.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def menu_comprar(texto):
        with open('textos/menu_comprar.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def exibir_servico(texto):
        with open('textos/exibir_servico.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def mensagem_comprou(texto):
        with open('textos/mensagem_comprou.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def termos(texto):
        with open('textos/termos.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def ajuda(texto):
        with open('textos/ajuda.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def id(texto):
        with open('textos/id.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def afiliados(texto):
        with open('textos/afiliados.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def saldo(texto):
        with open('textos/saldo.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    
    def verificacao_canal(texto):
        with open('textos/verificacao_canal.txt', 'w', encoding='utf-8') as f:
            f.write(texto)

class Botoes():
    def comprar():
        with open('botoes/comprar.txt', 'r', encoding='utf-8') as f:
              return f.read()
    def perfil():
        with open('botoes/perfil.txt', 'r', encoding='utf-8') as f:
            return f.read()
    def addsaldo():
        with open('botoes/addsaldo.txt', 'r', encoding='utf-8') as f:
            return f.read()
    def suporte():
        with open('botoes/suporte.txt', 'r', encoding='utf-8') as f:
            return f.read()
    def voltar():
        with open('botoes/voltar.txt', 'r', encoding='utf-8') as f:
            return f.read()
    def comprar_login():
        with open('botoes/comprar_loguin.txt', 'r', encoding='utf-8') as f:
            return f.read()
    def pesquisar_numero():
        with open('botoes/pesquisar.txt', 'r', encoding='utf-8') as f:
            return f.read()
    def pix_manual():
        with open('botoes/pix_manual.txt', 'r', encoding='utf-8') as f:
            return f.read()
    def pix_automatico():
        with open('botoes/pix_automatico.txt', 'r', encoding='utf-8') as f:
            return f.read()
    def download_historico():
        with open('botoes/download_historico.txt', 'r', encoding='utf-8') as f:
            return f.read()
    def trocar_pontos_por_saldo():
        with open('botoes/trocar_pontos_por_saldo.txt', 'r', encoding='utf-8') as f:
            return f.read()
    def paises():
        with open('botoes/paises.txt', 'r', encoding='utf-8') as f:
            return f.read()
    def aguardando_pagamento():
        try:
            with open('botoes/aguardando_pagamento.txt', 'r', encoding='utf-8') as f:
                return f.read()
        except:
            with open('botoes/aguardando_pagamnto.txt', 'w', encoding='utf-8') as f:
                f.write('⏰ AGUARDANDO PAGAMENTO')
                return '⏰ AGUARDANDO PAGAMENTO'

class MudarBotao():
    def paises(texto):
        with open('botoes/paises.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def comprar(texto):
        with open('botoes/comprar.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def perfil(texto):
        with open('botoes/perfil.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def addsaldo(texto):
        with open('botoes/addsaldo.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def suporte(texto):
        with open('botoes/suporte.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def voltar(texto):
        with open('botoes/voltar.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def comprar_login(texto):
        with open('botoes/comprar_login.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def pix_manual(texto):
        with open('botoes/pix_manual.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def pix_automatico(texto):
        with open('botoes/pix_automatico.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def download_historico(texto):
        with open('botoes/download_historico.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def trocar_pontos_por_saldo(texto):
        with open('botoes/trocar_pontos_por_saldo.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
    def aguardando_pagamento(texto):
        with open('botoes/aguardando_pagamento.txt', 'w', encoding='utf-8') as f:
            f.write(texto)

class Log():
    @staticmethod
    def mascarar_numero(numero):
        if not numero:
            return "N/D"
        s = str(numero).strip()
        if len(s) <= 4:
            return "*" * len(s)
        return f"{s[:-4]}****"
    
    @staticmethod
    def log_cancelamento_auto(chat_id, id_ativacao, servico, numero, valor, tempo):
        """Gera log de cancelamento automático por timeout"""
        numero_mascarado = Log.mascarar_numero(numero)
        return (
            f"⏰ <b>CANCELAMENTO AUTOMÁTICO</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{chat_id}</code>\n"
            f"🆔 <b>Ativação:</b> <code>{id_ativacao}</code>\n"
            f"📱 <b>Serviço:</b> {servico}\n"
            f"📞 <b>Número:</b> <code>{numero_mascarado}</code>\n"
            f"💰 <b>Valor estornado:</b> R${float(valor):.2f}\n"
            f"⏱️ <b>Tempo:</b> {tempo} minutos\n"
            f"📅 <b>Data:</b> {ViewTime.data_atual()} às {ViewTime.hora_atual()}"
        )
    
    @staticmethod
    def log_cancelamento_manual(chat_id, id_ativacao, servico, numero, valor):
        """Gera log de cancelamento manual pelo usuário"""
        numero_mascarado = Log.mascarar_numero(numero)
        return (
            f"👤 <b>CANCELAMENTO MANUAL</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{chat_id}</code>\n"
            f"🆔 <b>Ativação:</b> <code>{id_ativacao}</code>\n"
            f"📱 <b>Serviço:</b> {servico}\n"
            f"📞 <b>Número:</b> <code>{numero_mascarado}</code>\n"
            f"💰 <b>Valor estornado:</b> R${float(valor):.2f}\n"
            f"📅 <b>Data:</b> {ViewTime.data_atual()} às {ViewTime.hora_atual()}"
        )
    
    @staticmethod
    def log_sms_recebido(chat_id, servico, numero, codigo, valor):
        """Gera log de SMS recebido"""
        numero_mascarado = Log.mascarar_numero(numero)
        return (
            f"📨 <b>SMS RECEBIDO</b>\n\n"
            f"👤 <b>Usuário:</b> <code>{chat_id}</code>\n"
            f"📱 <b>Serviço:</b> {servico}\n"
            f"📞 <b>Número:</b> <code>{numero_mascarado}</code>\n"
            f"🔑 <b>Código:</b> <code>{codigo}</code>\n"
            f"💰 <b>Valor:</b> R${float(valor):.2f}\n"
            f"?? <b>Data:</b> {ViewTime.data_atual()} às {ViewTime.hora_atual()}"
        )

    @staticmethod
    def validar_destino(destino_id):
        if not destino_id or destino_id in ["SEUID", "ID", "", "0"]:
            return False, "Inválido", None
        
        try:
            if isinstance(destino_id, str) and destino_id.startswith('@'):
                return True, "Canal (username)", destino_id
            
            id_num = int(destino_id)
            
            if id_num < 0:
                return True, "Grupo/Supergrupo", id_num
            elif id_num > 0:
                return True, "Canal/Usuário", id_num
            else:
                return False, "ID zero inválido", None
                
        except (ValueError, TypeError):
            return False, "Formato inválido", None
    
    def destino_log_registro():
        canais = LogManager.obter_todos_canais('log-registro')
        if len(canais) == 1:
            return canais[0]
        return canais
    
    def destino_log_compra():
        canais = LogManager.obter_todos_canais('log-compra')
        if len(canais) == 1:
            return canais[0]
        return canais
    
    def destino_log_recarga():
        canais = LogManager.obter_todos_canais('log-recarga')
        if len(canais) == 1:
            return canais[0]
        return canais
    
    def destino_log_recebeusms():
        canais = LogManager.obter_todos_canais('log-recebeu-sms')
        if len(canais) == 1:
            return canais[0]
        return canais
    
    def destino_log_cancelousms():
        canais = LogManager.obter_todos_canais('log-cancelou-sms')
        if len(canais) == 1:
            return canais[0]
        return canais
    def log_registro(message):
        print(f"[API LOG] Gerando mensagem de log de registro...")
        try:
            with open('log/registro.txt', 'r', encoding='utf-8') as f:
                txt = f.read()
            print(f"[API LOG] Template carregado: {txt[:50]}...")
            
            if message == None:
                print(f"[API LOG] ⚠️ Message é None, retornando template vazio")
                return txt
            
            id = message.chat.id
            name = message.chat.first_name if hasattr(message.chat, 'first_name') and message.chat.first_name else message.from_user.first_name if hasattr(message, 'from_user') and message.from_user.first_name else "Sem nome"
            username = message.from_user.username if hasattr(message, 'from_user') and message.from_user.username else message.chat.username if hasattr(message.chat, 'username') and message.chat.username else "sem_username"
            link = f'https://t.me/{username}' if username != "sem_username" else "Sem link"
            
            print(f"[API LOG] Dados extraídos - ID: {id}, Nome: {name}, Username: {username}")
            
            texto = txt.replace('{id}', f'{id}').replace('{name}', f'{name}').replace('{username}', f'@{username}').replace('{link}', f'{link}').replace('\\n', '\n')
            print(f"[API LOG] Mensagem gerada com sucesso (tamanho: {len(texto)} chars)")
            return texto
        except Exception as e:
            print(f"[API LOG] ❌ Erro ao gerar log_registro: {e}")
            import traceback
            print(f"[API LOG] Traceback completo:\n{traceback.format_exc()}")
            return f"Erro ao gerar log: {e}"
    def log_compra(chat_id, nome, numero, operadora, valor):
        with open('log/compra.txt', 'r', encoding='utf-8') as f:
            texto = f.read()
        saldo = InfoUser.saldo(chat_id)
        numero_mascarado = Log.mascarar_numero(numero)
        texto = texto.replace('{id}', f'{chat_id}').replace('{servico}', f'{nome}').replace('{valor}', f'{float(valor):.2f}').replace('{saldo}', f'{saldo:.2f}').replace('{numero}', f'{numero_mascarado}').replace('{operadora}', f'{operadora}').replace('\\n', '\n')
        return texto
    def log_recarga(message, id_pagamento, valor):
        with open('log/recarga.txt', 'r', encoding='utf-8') as f:
            txt = f.read()
        if message == None:
            return txt
        id = message.chat.id
        name = message.chat.first_name
        username = message.chat.username
        link = f'https://t.me/{username}'
        data = ViewTime.data_atual()
        hora = ViewTime.hora_atual()
        saldo = InfoUser.saldo(message.chat.id)
        texto = txt.replace('{id}', f'{id}').replace('{name}', f'{name}').replace('{username}', f'@{username}').replace('{link}', f'{link}').replace('{data}', f'{data}').replace('{hora}', f'{hora}').replace('{id_pagamento}', f'{id_pagamento}').replace('{valor}', f'{float(valor):.2f}').replace('{saldo}', f'{float(saldo):.2f}').replace('\\n', '\n')
        return texto

class LogManager():
    """Classe para gerenciar múltiplos canais de log"""
    
    TIPOS_LOG = {
        'log-registro': 'Log de Registro',
        'log-compra': 'Log de Compra',
        'log-recarga': 'Log de Recarga',
        'log-recebeu-sms': 'Log de SMS Recebido',
        'log-cancelou-sms': 'Log de SMS Cancelado',
        'log-auditoria': 'Log de Auditoria'
    }
    
    @staticmethod
    def carregar_destinos():
        try:
            with open('settings/destino_logs.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar destinos de log: {e}")
            return {tipo: [] for tipo in LogManager.TIPOS_LOG.keys()}
    
    @staticmethod
    def salvar_destinos(data):
        try:
            with open('settings/destino_logs.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar destinos de log: {e}")
            return False
    
    @staticmethod
    def adicionar_canal(tipo_log, canal_id):
        if tipo_log not in LogManager.TIPOS_LOG:
            return False, "Tipo de log inválido"
        
        valido, tipo, id_convertido = Log.validar_destino(canal_id)
        if not valido:
            return False, f"Canal inválido: {tipo}"
        
        destinos = LogManager.carregar_destinos()
        
        if tipo_log not in destinos:
            destinos[tipo_log] = []
        elif not isinstance(destinos[tipo_log], list):
            destinos[tipo_log] = [destinos[tipo_log]] if destinos[tipo_log] else []
        
        canal_str = str(canal_id)
        if canal_str in destinos[tipo_log]:
            return False, "Canal já cadastrado neste tipo de log"
        
        destinos[tipo_log].append(canal_str)
        
        if LogManager.salvar_destinos(destinos):
            return True, f"Canal adicionado com sucesso ao {LogManager.TIPOS_LOG[tipo_log]}"
        else:
            return False, "Erro ao salvar configuração"
    
    @staticmethod
    def remover_canal(tipo_log, canal_id):
        if tipo_log not in LogManager.TIPOS_LOG:
            return False, "Tipo de log inválido"
        
        destinos = LogManager.carregar_destinos()
        
        if tipo_log not in destinos or not isinstance(destinos[tipo_log], list):
            return False, "Nenhum canal cadastrado neste tipo de log"
        
        canal_str = str(canal_id)
        if canal_str not in destinos[tipo_log]:
            return False, "Canal não encontrado"
        
        destinos[tipo_log].remove(canal_str)
        
        if LogManager.salvar_destinos(destinos):
            return True, f"Canal removido com sucesso do {LogManager.TIPOS_LOG[tipo_log]}"
        else:
            return False, "Erro ao salvar configuração"
    
    @staticmethod
    def listar_canais(tipo_log):
        if tipo_log not in LogManager.TIPOS_LOG:
            return None
        
        destinos = LogManager.carregar_destinos()
        
        if tipo_log not in destinos:
            return []
        
        if isinstance(destinos[tipo_log], list):
            return destinos[tipo_log]
        else:
            return [destinos[tipo_log]] if destinos[tipo_log] else []
    
    @staticmethod
    def obter_todos_canais(tipo_log):
        canais = LogManager.listar_canais(tipo_log)
        if not canais:
            return []
        return canais
    
    @staticmethod
    def formatar_lista_canais(tipo_log):
        canais = LogManager.listar_canais(tipo_log)
        
        if not canais:
            return f"📋 <b>{LogManager.TIPOS_LOG[tipo_log]}</b>\n\n❌ Nenhum canal cadastrado"
        
        texto = f"📋 <b>{LogManager.TIPOS_LOG[tipo_log]}</b>\n\n"
        texto += f"📊 Total: {len(canais)} canal(is)\n\n"
        
        for i, canal in enumerate(canais, 1):
            valido, tipo, _ = Log.validar_destino(canal)
            tipo_str = tipo if valido else "Inválido"
            texto += f"{i}. <code>{canal}</code>\n   └ {tipo_str}\n"
        
        return texto

class MudarLog():
    def log_registro(txt):
        with open('log/registro.txt', 'w', encoding='utf-8') as f:
            f.write(txt)
    def log_compra(txt):
        with open('log/compra.txt', 'w', encoding='utf-8') as f:
            f.write(txt)
    def log_recarga(txt):
        with open('log/recarga.txt', 'w', encoding='utf-8') as f:
            f.write(txt)

class CriarPix():
    def CriarPixGn(message, valor):
        response = gerar_cobranca.gerar_pix(f'{float(valor):.2f}', message.chat.id)
        locationId = response["locationId"]
        pix_qr = response["code"]
        link_pag = response["link"]
        txid = response["txid"]
        return locationId, pix_qr, link_pag, txid
    def VerificarPixGn(txid):
        params = {
            'txid': txid
            }
        response =  gn.pix_detail_charge(params=params)
        status = response["status"]
        if status == "CONCLUIDA":
            return True
        else:
            return False
    
    # ==================== NOVO: CRIAR PIX ZUCPAY ====================
    def CriarPixZucpay(valor, id_usuario):
        try:
            zucpay = ApiZucpayInfo()
            return zucpay.criar_pagamento_pix(valor, id_usuario)
        except Exception as e:
            print(f"❌ Erro ao criar PIX Zucpay: {e}")
            return None

    def VerificarPixZucpay(transaction_id):
        try:
            zucpay = ApiZucpayInfo()
            status = zucpay.verificar_pagamento(transaction_id)
            if status == "paid":
                return True
            return False
        except Exception as e:
            print(f"❌ Erro ao verificar Zucpay: {e}")
            return False

    def CriarPixUnificado(valor, id_usuario, plataforma=None):
        if plataforma is None:
            plataforma = CredentialsChange.PlataformaPix.plataforma_padrao()
        
        if plataforma == "zucpay" and CredentialsChange.PlataformaPix.status_zucpay():
            return CriarPix.CriarPixZucpay(valor, id_usuario)
        else:
            if CredentialsChange.PlataformaPix.status_zucpay():
                return CriarPix.CriarPixZucpay(valor, id_usuario)
            else:
                raise Exception("Nenhuma plataforma de pagamento disponível")

class ApiUnificada:
    def verificar_pagamento_unificado(payment_id, plataforma):
        if plataforma == "zucpay":
            return CriarPix.VerificarPixZucpay(payment_id)
        else:
            return False

# ==================== SISTEMA DE COOLDOWN (CORRIGIDO) ====================
class SmsCooldown:
    def __init__(self):
        self.cooldowns = {}
        self.cooldown_duration = 120

    def can_request_sms(self, user_id, service_id):
        if not CooldownCancelamento.ativado():
            return True
        
        if user_id not in self.cooldowns:
            return True
        
        if service_id not in self.cooldowns[user_id]:
            return True
        
        current_time = time.time()
        last_request_time = self.cooldowns[user_id][service_id]
        
        return (current_time - last_request_time) >= self.cooldown_duration

    def get_remaining_time(self, user_id, service_id):
        if user_id not in self.cooldowns or service_id not in self.cooldowns[user_id]:
            return 0
        
        current_time = time.time()
        last_request_time = self.cooldowns[user_id][service_id]
        elapsed_time = current_time - last_request_time
        
        if elapsed_time >= self.cooldown_duration:
            return 0
        
        return int(self.cooldown_duration - elapsed_time)

    def add_cooldown(self, user_id, service_id):
        if user_id not in self.cooldowns:
            self.cooldowns[user_id] = {}
        
        self.cooldowns[user_id][service_id] = time.time()

    def clear_cooldown(self, user_id, service_id=None):
        if user_id in self.cooldowns:
            if service_id is None:
                del self.cooldowns[user_id]
            elif service_id in self.cooldowns[user_id]:
                del self.cooldowns[user_id][service_id]
                if not self.cooldowns[user_id]:
                    del self.cooldowns[user_id]

sms_cooldown = SmsCooldown()

class CooldownCancelamento:
    ARQUIVO_CONFIG = "settings/cooldown_config.json"
    _lock = threading.Lock()

    @staticmethod
    def carregar_config():
        try:
            with open(CooldownCancelamento.ARQUIVO_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"ativado": True, "tempo_espera_segundos": 120}
        except Exception:
            return {"ativado": True, "tempo_espera_segundos": 120}

    @staticmethod
    def salvar_config(config):
        with CooldownCancelamento._lock:
            try:
                with open(CooldownCancelamento.ARQUIVO_CONFIG, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                print(f"Erro ao salvar config cooldown: {e}")
                return False

    @staticmethod
    def ativado():
        config = CooldownCancelamento.carregar_config()
        return config.get("ativado", True)

    @staticmethod
    def tempo_espera():
        config = CooldownCancelamento.carregar_config()
        return config.get("tempo_espera_segundos", 120)

    @staticmethod
    def alternar_status():
        config = CooldownCancelamento.carregar_config()
        config["ativado"] = not config.get("ativado", True)
        return CooldownCancelamento.salvar_config(config)

    @staticmethod
    def mudar_tempo_espera(novos_segundos):
        if novos_segundos < 0:
            return False
        config = CooldownCancelamento.carregar_config()
        config["tempo_espera_segundos"] = novos_segundos
        return CooldownCancelamento.salvar_config(config)

class LimiteGeracao:
    ARQUIVO_CONFIG = "settings/limite_geracao_config.json"
    ARQUIVO_TENTATIVAS = "settings/tentativas_usuario.json"
    _lock = threading.Lock()

    @staticmethod
    def carregar_config():
        try:
            with open(LimiteGeracao.ARQUIVO_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "ativado": True,
                "max_tentativas_consecutivas": 8,
                "tempo_minimo_entre_geracoes": 30,
                "tempo_ban_minutos": 15,
                "tempo_ban_progressivo": True,
                "max_tempo_ban_minutos": 240,
                "apenas_constantes": False
            }
        except Exception:
            return {
                "ativado": True,
                "max_tentativas_consecutivas": 8,
                "tempo_minimo_entre_geracoes": 30,
                "tempo_ban_minutos": 15,
                "tempo_ban_progressivo": True,
                "max_tempo_ban_minutos": 240,
                "apenas_constantes": False
            }

    @staticmethod
    def salvar_config(config):
        with LimiteGeracao._lock:
            try:
                with open(LimiteGeracao.ARQUIVO_CONFIG, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                print(f"❌ Erro ao salvar config limite geracao: {e}")
                return False

    @staticmethod
    def carregar_tentativas():
        try:
            with open(LimiteGeracao.ARQUIVO_TENTATIVAS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception:
            return {}

    @staticmethod
    def salvar_tentativas(tentativas):
        with LimiteGeracao._lock:
            try:
                with open(LimiteGeracao.ARQUIVO_TENTATIVAS, 'w', encoding='utf-8') as f:
                    json.dump(tentativas, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                print(f"❌ Erro ao salvar tentativas: {e}")
                return False

    @staticmethod
    def ativado():
        config = LimiteGeracao.carregar_config()
        return config.get("ativado", True)

    @staticmethod
    def apenas_constantes():
        config = LimiteGeracao.carregar_config()
        return config.get("apenas_constantes", False)

    @staticmethod
    def _garantir_estrutura_usuario(user_data):
        campos_defaults = {
            "attempts_count": 0,
            "last_request_at": None,
            "blocked_until": None,
            "ban_count": 0,
            "last_sms_received_at": None
        }
        for campo, valor_padrao in campos_defaults.items():
            if campo not in user_data:
                user_data[campo] = valor_padrao
        return user_data

    @staticmethod
    def registrar_tentativa(user_id):
        config = LimiteGeracao.carregar_config()
        tentativas = LimiteGeracao.carregar_tentativas()
        user_id_str = str(user_id)
        tempo_atual = time.time()
        tempo_minimo = config.get("tempo_minimo_entre_geracoes", 30)
        max_tentativas = config.get("max_tentativas_consecutivas", 8)

        if user_id_str not in tentativas:
            tentativas[user_id_str] = {
                "attempts_count": 0,
                "last_request_at": None,
                "blocked_until": None,
                "ban_count": 0,
                "last_sms_received_at": None
            }

        user_data = tentativas[user_id_str]
        user_data = LimiteGeracao._garantir_estrutura_usuario(user_data)
        tentativas[user_id_str] = user_data

        last_request = user_data.get("last_request_at")

        if last_request and (tempo_atual - last_request) >= tempo_minimo:
            tempo_passado = int(tempo_atual - last_request)
            print(f"✅ [LIMITE] User {user_id} aguardou {tempo_passado}s (mínimo: {tempo_minimo}s) - CONTADOR RESETADO")
            user_data["attempts_count"] = 0

        user_data["attempts_count"] += 1
        user_data["last_request_at"] = tempo_atual

        tentativas_atuais = user_data['attempts_count']
        tentativas_restantes = max_tentativas - tentativas_atuais
        print(f"📊 [LIMITE] User {user_id}: {tentativas_atuais}/{max_tentativas} tentativas | Faltam {tentativas_restantes} até bloqueio")

        LimiteGeracao.salvar_tentativas(tentativas)
    
    @staticmethod
    def reseta_tentativas(user_id):
        tentativas = LimiteGeracao.carregar_tentativas()
        user_id_str = str(user_id)

        if user_id_str in tentativas:
            user_data = tentativas[user_id_str]
            user_data = LimiteGeracao._garantir_estrutura_usuario(user_data)
            tentativas[user_id_str] = user_data

            tentativas_antes = user_data.get("attempts_count", 0)
            user_data["attempts_count"] = 0
            user_data["last_sms_received_at"] = time.time()
            user_data["blocked_until"] = None
            print(f"✅ [LIMITE] User {user_id} RECEBEU SMS - Contador resetado de {tentativas_antes} → 0 e bloqueio removido")
            LimiteGeracao.salvar_tentativas(tentativas)
        else:
            print(f"ℹ️  [LIMITE] User {user_id} recebeu SMS mas não tem histórico de tentativas")
            
    @staticmethod
    def pode_gerar(user_id, eh_constante_func=None):
        if not LimiteGeracao.ativado():
            print(f"ℹ️  [LIMITE] Sistema DESATIVADO - User {user_id} liberado")
            return True, None

        config = LimiteGeracao.carregar_config()
        tentativas = LimiteGeracao.carregar_tentativas()
        user_id_str = str(user_id)
        max_tentativas = config.get("max_tentativas_consecutivas", 8)
        tempo_ban_base = config.get("tempo_ban_minutos", 15)
        ban_progressivo = config.get("tempo_ban_progressivo", True)
        max_ban = config.get("max_tempo_ban_minutos", 240)
        apenas_constantes = config.get("apenas_constantes", False)

        if apenas_constantes and eh_constante_func:
            if not eh_constante_func(user_id):
                print(f"ℹ️  [LIMITE] User {user_id} é constante - limite não se aplica")
                return True, None

        if user_id_str not in tentativas:
            print(f"ℹ️  [LIMITE] User {user_id} - Primeira geração, nenhuma tentativa anterior")
            return True, None

        user_data = tentativas[user_id_str]
        user_data = LimiteGeracao._garantir_estrutura_usuario(user_data)
        tentativas[user_id_str] = user_data

        tempo_atual = time.time()

        blocked_until = user_data.get("blocked_until")
        if blocked_until and tempo_atual < blocked_until:
            tempo_restante = int(blocked_until - tempo_atual)
            ban_count = user_data.get("ban_count", 0)

            if tempo_restante >= 60:
                tempo_str = f"{int(tempo_restante / 60)} minuto(s)"
            else:
                tempo_str = f"{tempo_restante} segundo(s)"

            print(f"🚫 [LIMITE] User {user_id} BLOQUEADO - Ban #{ban_count} | Tempo restante: {tempo_str}")

            return False, (
                f"⚠️ <b>BLOQUEIO TEMPORÁRIO</b>\n\n"
                f"🚫 Limite de gerações atingido\n"
                f"⏰ Aguarde <b>{tempo_str}</b> para gerar novamente."
            )

        if blocked_until and tempo_atual >= blocked_until:
            user_data["blocked_until"] = None
            user_data["attempts_count"] = 0
            print(f"✅ [LIMITE] User {user_id} - Bloqueio EXPIRADO, liberado para gerar novamente")
            LimiteGeracao.salvar_tentativas(tentativas)
            return True, None

        attempts = user_data.get("attempts_count", 0)

        if attempts >= max_tentativas:
            ban_count = user_data.get("ban_count", 0)

            if ban_progressivo:
                tempo_ban = min(tempo_ban_base * (2 ** ban_count), max_ban)
            else:
                tempo_ban = tempo_ban_base

            blocked_until = tempo_atual + (tempo_ban * 60)
            user_data["blocked_until"] = blocked_until
            user_data["ban_count"] = ban_count + 1
            user_data["attempts_count"] = 0

            ban_tipo = "Progressivo" if ban_progressivo else "Fixo"
            print(f"🚫 [LIMITE] User {user_id} BLOQUEADO APLICADO!")
            print(f"   ├─ Tentativas: {attempts}/{max_tentativas}")
            print(f"   ├─ Ban #{ban_count + 1}: {tempo_ban} minuto(s) ({ban_tipo})")
            print(f"   └─ Desbloqueio em: {int(tempo_ban * 60)} segundos")

            LimiteGeracao.salvar_tentativas(tentativas)

            return False, (
                f"⚠️ <b>LIMITE ATINGIDO</b>\n\n"
                f"🚫 Você atingiu o limite de <b>{max_tentativas} gerações</b>!\n"
                f"⏰ Penalização: <b>{tempo_ban} minuto(s)</b>"
            )

        return True, None

    @staticmethod
    def obter_info_usuario(user_id):
        tentativas = LimiteGeracao.carregar_tentativas()
        user_id_str = str(user_id)
        config = LimiteGeracao.carregar_config()
        tempo_atual = time.time()

        if user_id_str not in tentativas:
            return {
                "attempts_count": 0,
                "max_tentativas": config.get("max_tentativas_consecutivas", 8),
                "blocked": False,
                "tempo_restante_segundos": 0,
                "tempo_restante_minutos": 0,
                "ban_count": 0
            }

        user_data = tentativas[user_id_str]
        blocked_until = user_data.get("blocked_until")

        blocked = False
        tempo_seg = 0
        tempo_min = 0

        if blocked_until and tempo_atual < blocked_until:
            blocked = True
            tempo_seg = int(blocked_until - tempo_atual)
            tempo_min = int(tempo_seg / 60) + 1

        return {
            "attempts_count": user_data.get("attempts_count", 0),
            "max_tentativas": config.get("max_tentativas_consecutivas", 8),
            "blocked": blocked,
            "tempo_restante_segundos": tempo_seg,
            "tempo_restante_minutos": tempo_min,
            "ban_count": user_data.get("ban_count", 0)
        }

class BroadcastMessage:
    @staticmethod
    def carregar_broadcasts():
        try:
            print("🔍 [API] Carregando broadcasts...")
            with open('settings/broadcast_groups.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                broadcasts = data.get('broadcasts', [])
                print(f"✅ [API] {len(broadcasts)} broadcasts carregados")
                return broadcasts
        except Exception as e:
            print(f"❌ [API] Erro ao carregar broadcasts: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def salvar_broadcasts(broadcasts):
        try:
            print(f"💾 [API] Salvando {len(broadcasts)} broadcasts...")
            with open('settings/broadcast_groups.json', 'w', encoding='utf-8') as f:
                json.dump({'broadcasts': broadcasts}, f, indent=2, ensure_ascii=False)
            print(f"✅ [API] Broadcasts salvos com sucesso")
            return True
        except Exception as e:
            print(f"❌ [API] Erro ao salvar broadcasts: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def criar_broadcast(nome, mensagem, grupos_destino, imagem_file_id=None, intervalo_minutos=120, ativo=True):
        try:
            print(f"📝 [API] Criando novo broadcast: {nome} (intervalo: {intervalo_minutos}min, grupos: {len(grupos_destino)})...")

            broadcasts = BroadcastMessage.carregar_broadcasts()

            novo_broadcast = {
                'id': int(time.time() * 1000),
                'nome': nome,
                'mensagem': mensagem,
                'imagem_file_id': imagem_file_id,
                'intervalo_minutos': intervalo_minutos,
                'grupos_destino': grupos_destino,
                'ativo': ativo,
                'criado_em': datetime.now().isoformat(),
                'ultimo_envio': None
            }

            broadcasts.append(novo_broadcast)

            if BroadcastMessage.salvar_broadcasts(broadcasts):
                print(f"✅ [API] Broadcast criado com sucesso! ID: {novo_broadcast['id']}")
                return novo_broadcast
            else:
                print(f"❌ [API] Erro ao salvar broadcast na lista")
                return None
        except Exception as e:
            print(f"❌ [API] ERRO ao criar broadcast: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def obter_broadcast(broadcast_id):
        broadcasts = BroadcastMessage.carregar_broadcasts()
        for broadcast in broadcasts:
            if broadcast['id'] == broadcast_id:
                return broadcast
        return None

    @staticmethod
    def atualizar_broadcast(broadcast_id, **kwargs):
        broadcasts = BroadcastMessage.carregar_broadcasts()

        for i, broadcast in enumerate(broadcasts):
            if broadcast['id'] == broadcast_id:
                broadcast.update(kwargs)
                broadcasts[i] = broadcast
                return BroadcastMessage.salvar_broadcasts(broadcasts)
        return False

    @staticmethod
    def deletar_broadcast(broadcast_id):
        broadcasts = BroadcastMessage.carregar_broadcasts()
        broadcasts = [b for b in broadcasts if b['id'] != broadcast_id]
        return BroadcastMessage.salvar_broadcasts(broadcasts)

    @staticmethod
    def toggle_ativo(broadcast_id):
        broadcast = BroadcastMessage.obter_broadcast(broadcast_id)
        if broadcast:
            return BroadcastMessage.atualizar_broadcast(broadcast_id, ativo=not broadcast['ativo'])
        return False

    @staticmethod
    def adicionar_grupo(broadcast_id, grupo_id):
        broadcast = BroadcastMessage.obter_broadcast(broadcast_id)
        if broadcast:
            if grupo_id not in broadcast['grupos_destino']:
                broadcast['grupos_destino'].append(grupo_id)
                return BroadcastMessage.atualizar_broadcast(broadcast_id, grupos_destino=broadcast['grupos_destino'])
        return False

    @staticmethod
    def remover_grupo(broadcast_id, grupo_id):
        broadcast = BroadcastMessage.obter_broadcast(broadcast_id)
        if broadcast:
            if grupo_id in broadcast['grupos_destino']:
                broadcast['grupos_destino'].remove(grupo_id)
                return BroadcastMessage.atualizar_broadcast(broadcast_id, grupos_destino=broadcast['grupos_destino'])
        return False

    @staticmethod
    def atualizar_ultimo_envio(broadcast_id):
        return BroadcastMessage.atualizar_broadcast(broadcast_id, ultimo_envio=datetime.now().isoformat())

class BroadcastDelivery:
    @staticmethod
    def carregar_entregas():
        try:
            with open('database/broadcast_delivery.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('deliveries', [])
        except Exception as e:
            print(f"Erro ao carregar entregas de divulgação: {e}")
            return []

    @staticmethod
    def salvar_entregas(entregas):
        try:
            with open('database/broadcast_delivery.json', 'w', encoding='utf-8') as f:
                json.dump({'deliveries': entregas}, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar entregas de divulgação: {e}")
            return False

    @staticmethod
    def registrar_entrega(broadcast_id, grupo_id, sucesso=True, erro_msg=None):
        entregas = BroadcastDelivery.carregar_entregas()

        registro = {
            'broadcast_id': broadcast_id,
            'grupo_id': grupo_id,
            'timestamp': datetime.now().isoformat(),
            'sucesso': sucesso,
            'erro': erro_msg
        }

        entregas.append(registro)
        if len(entregas) > 10000:
            entregas = entregas[-10000:]

        BroadcastDelivery.salvar_entregas(entregas)

    @staticmethod
    def obter_estatisticas_grupo(grupo_id):
        entregas = BroadcastDelivery.carregar_entregas()
        grupo_entregas = [e for e in entregas if e['grupo_id'] == grupo_id]

        if not grupo_entregas:
            return {'total': 0, 'sucesso': 0, 'erro': 0}

        sucesso = len([e for e in grupo_entregas if e['sucesso']])
        erro = len(grupo_entregas) - sucesso

        return {
            'total': len(grupo_entregas),
            'sucesso': sucesso,
            'erro': erro
        }
