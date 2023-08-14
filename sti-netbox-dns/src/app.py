import requests
import json

from walkoff_app_sdk.app_base import AppBase

STATUS_SUCCESS = (200,201,204)

class NetboxDNSApp(AppBase):
    __version__ = "1.0.0"
    app_name = "Netbox DNS App"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
                
        super().__init__(redis, logger, console_logger)
        self.token = None
    
    def obter_url(self, server, url):
        return "http://{}:8888/api/{}".format(server,url)
    
    def obter_header(self, token):
        return {"Content-Type": "application/json",
                "Authorization": "Token {}".format(token) }
    
    def obter_nameservers(self, nameservers):
        nameserverlist = []
        if nameservers:
            for nameserver in nameservers.split(";"):
                nameserverlist.append({"name":nameserver})
        return nameserverlist
        

    ################################################# metodos dos api.yaml ############################################
    
    # del_zona
    def remover_zona(self, server, token, chamado, zona):
        try:
            api_url = self.obter_url(server,"plugins/netbox-dns/zones/")
            header = self.obter_header(token)

            #obter a zona no netbox
            get = requests.get(api_url+"?name="+zona,headers=header,verify=False)

            #Se encontrou a zona continua
            if get.status_code in STATUS_SUCCESS:
                #url do patch e do delete é a mesma
                url = f"{api_url}{get.json()['results'][0]['id']}/"

                #atualiza a zona com o chamado de remoção
                atualizar_chamado = {"custom_fields":{"chamado":chamado}}
                patch = requests.patch(url,headers=header,json=atualizar_chamado,verify=False)

                # se atualizou continua
                if patch.status_code in STATUS_SUCCESS:
                    #deleta a zona
                    delete = requests.delete(url,headers=header,verify=False)

                    # se deletou tudo certo!
                    if delete.status_code in STATUS_SUCCESS:
                        return json.dumps({"success": True, "message":delete.text, "zona":zona, "chamado": chamado})
                    else:
                        return json.dumps({"success": False, "message":delete.text})
                else:
                    return json.dumps({"success": False, "message":patch.text})
            else:
                return json.dumps({"success": False, "message":get.text})
            
        except Exception as e:
            return json.dumps({"success": False, "message":e})
        
    # add_zona
    def adicionar_zona(
        self, server, token, zona, chamado, nameservers, descricao, soa_serial, status="active", default_ttl=86400, soa_ttl=86400, soa_mname=1, soa_rname="sti@ufrn.br", soa_refresh=172800, soa_retry=7200, soa_expire=2592000, soa_minimum=3600
    ):  
        try:
            api_url = self.obter_url(server,"plugins/netbox-dns/zones/")
            header = self.obter_header(token)



            data = { "name": zona,
                     "nameservers": self.obter_nameservers(nameservers),
                     "status": status if status else "active",
                     "description": descricao,
                     "default_ttl": default_ttl if default_ttl else 86400,
                     "soa_ttl": soa_ttl if soa_ttl else 86400,
                     "soa_mname": soa_mname if soa_mname else 1,
                     "soa_rname": soa_rname if soa_rname else "sti@ufrn.br",
                     "soa_serial": soa_serial,
                     "soa_serial_auto": False,
                     "soa_refresh": soa_refresh if soa_refresh else 172800,
                     "soa_retry": soa_retry if soa_retry else 7200,
                     "soa_expire": soa_expire if soa_expire else 2592000,
                     "soa_minimum": soa_minimum if soa_minimum else 3600,
                     "custom_fields": {"chamado":chamado}
                    }

            response = requests.post(api_url,headers=header,json=data, verify=False)

            if response.status_code in STATUS_SUCCESS:
                return json.dumps({"success": True, "message":response.json()})
            else:
                return json.dumps({"success": False, "message":response.text})
        
        except Exception as e:
            return json.dumps({"success": False, "message":e})

if __name__ == "__main__":
    NetboxDNSApp.run()
