import requests
import json

class CIP():
    urls = {
        "user_me" : "https://api.criminalip.io/v1/user/me",
        "ip_data" : "https://api.criminalip.io/v1/ip/data",
        "ip_summary" : "https://api.criminalip.io/v1/ip/summary",
        "ip_vpn" : "https://api.criminalip.io/v1/ip/vpn",
        "ip_hosting" : "https://api.criminalip.io/v1/ip/hosting",
        "banner_search" : "https://api.criminalip.io/v1/banner/search",
        "banner_stats" : "https://api.criminalip.io/v1/banner/stats",
        "domain_reports" : "https://api.criminalip.io/v1/domain/reports",
        "domain_report_id" : "https://api.criminalip.io/v1/domain/report/{}",
        "domain_scan" : "https://api.criminalip.io/v1/domain/scan"
    }

    def __init__(self, api_key):
        headers = {}
        headers["x-api-key"] = api_key
        self.headers = headers

    def json_prints(self, string):
        return json.dumps(json.loads(string), indent=2, sort_keys=True)

    def user_me(self):
        response = requests.request("POST", self.urls["user_me"], headers=self.headers)
        return self.json_prints(response.text)

    def ip_data(self, params):
        if len(params) < 1:
            return "IP Parameter is required"
        response = requests.request("GET", self.urls["ip_data"], headers=self.headers, params=params)
        return self.json_prints(response.text)

    def ip_summary(self, params):
        if len(params) < 1:
            return "IP Parameter is required"
        response = requests.request("GET", self.urls["ip_summary"], headers=self.headers, params=params)
        return self.json_prints(response.text)

    def ip_vpn(self, params):
        if len(params) < 1:
            return "IP Parameter is required"
        response = requests.request("GET", self.urls["ip_vpn"], headers=self.headers, params=params)
        return self.json_prints(response.text)

    def ip_summary(self, params):
        if len(params) < 1:
            return "IP Parameter is required"
        response = requests.request("GET", self.urls["ip_hosting"], headers=self.headers, params=params)
        return self.json_prints(response.text)

    def banner_search(self, params):
        if "query" not in params.keys():
            return "Query Parameter is required"
        if "offset" not in params.keys():
            return "Offset Parameter is required"
        response = requests.request("GET", self.urls["banner_search"], headers=self.headers, params=params)
        return self.json_prints(response.text)

    def banner_stats(self, params):
        if len(params) < 1:
            return "Query Parameter is required"
        response = requests.request("GET", self.urls["banner_stats"], headers=self.headers, params=params)
        return self.json_prints(response.text)

    def domain_reports(self, params):
        if len(params) < 1:
            return "Query Parameter is required"
        response = requests.request("GET", self.urls["domain_reports"], headers=self.headers, params=params)
        return self.json_prints(response.text)

    def domain_report(self, params):
        if len(params) < 1:
            return "Scan Id Parameter is required"
        response = requests.request("GET", self.urls["domain_report"], headers=self.headers, params=params)
        return self.json_prints(response.text)

    def domain_scan(self, params):
        if len(params) < 1:
            return "Query Parameter is required"
        response = requests.request("POST", self.urls["domain_scan"], headers=self.headers, params=params)
        return self.json_prints(response.text)


cip = CIP("IMtUEoSLkQGqwJTDRySasHevgwuEPd7uC9Ej1HcuNfu7IfukoSGVpkZYTeAK")
print(cip.banner_search({"query" : "ssh", "offset" : 0}))