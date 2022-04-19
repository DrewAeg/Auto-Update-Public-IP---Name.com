"""
This application is meant to automatically update the IP address for an `A` and `AAAA` record maintained by name.com.

"""

# Built-in Modules
import json
import time
import ipaddress
from datetime import datetime

# Downloaded Modules
import requests             # pip3 install requests
import dns.resolver         # pip3 install dnspython

# Local Modules
import configurations as c



class Record_Updater():

    def __init__(self):
        """
        An object for maintining a single FQDN on name.com
        """
        self.name_api_url = c.NAME_API_URL
        self.ip_api_url = c.IP_API_URL
        self.ip_api_key = c.IP_API_KEY
        self.current_ip = self.get_current_ip()
        self.dns_record_type = self.get_ip_type(self.current_ip)
        self.fqdn = c.FQDN
        self.domain = self.get_domain_from_fqdn(self.fqdn)
        self.ttl_override_value = c.TTL_VALUE
        self.dns_nameserver = c.NAMESERVER
        self.previous_ip = self.get_current_dns_resolution(self.fqdn, self.dns_nameserver, self.dns_record_type)


    def get_current_ip(self):
        """
        Uses the provided IP Lookup API endpoint to obtain the current IP address.

        Returns IP address as a string.
        """
        url = self.ip_api_url
        response = requests.request("GET", url)
        result = json.loads(response.text)
        return result[self.ip_api_key]


    def get_ip_type(self, address:str) -> str:
        """
        Determine which type of address a string is.

        Returns either `ipv4` or `ipv6` as a string.
        """
        try:
            ip = ipaddress.ip_address(address)
            if isinstance(ip, ipaddress.IPv4Address):
                return "A"
            elif isinstance(ip, ipaddress.IPv6Address):
                return "AAAA"
        except ValueError:
            print(f"{datetime.now()} :: `{address}` is an invalid IP address.  Could not dertime IP address type.")
            return None


    def get_current_dns_resolution(self, query:str="example.org", nameserver:str="8.8.8.8", qtype:str="A"):
        """
        Query a specific nameserver for:
        - An IPv4 address for a given hostname (qtype="A")
        - An IPv6 address for a given hostname (qtype="AAAA")
        
        Returns the IP address as a string.

        NOTE: May throw dns.resolver.NXDOMAIN, dns.resolver.NoAnswer or similar
        """
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [nameserver]
        try:
            answer = resolver.resolve(query, qtype)
        except Exception as error:
            print(f"{datetime.now()} :: ERROR: {error}")
            answer = ""
        if len(answer) == 0:
            return None
        else:
            return str(answer[0])


    def get_domain_from_fqdn(self, fqdn:str) -> str:
        """
        Find the domain from an FQDN.  
        Looks for the domain (example.org) from the FQDN (dev.test.example.org)

        Returns string with the domain.
        """
        count = fqdn.count(".")
        if count == 1:
            return str(fqdn)
        index = self.find_nth(fqdn, ".", count-1)
        domain = fqdn[index+1:]
        return domain

    
    def dns_updater(self) -> None:
        """
        Checks if the current IP and previous IP match.  If not, it updates the associated record.

        Returns None
        """
        if self.current_ip != self.previous_ip:
            self.update_dns_record()


    def update_dns_record(self) -> bool:
        """
        Updates the associated dns record on name.com.

        Returns bool, True for successful update, False for unsuccessful update.
        """
        record = self.get_dns_record_id()
        # If the record doesn't exist, don't try and update it.
        if record is None:
            return None
        # If the record exists, update it.
        record_id = record["id"]
        if c.TTL_OVERRIDE is False:
            record_ttl = record["ttl"]
        else:
            record_ttl = self.ttl_override_value
        url = f"{self.name_api_url}domains/{self.domain}/records/{record_id}"
        payload = json.dumps({
            "answer": self.current_ip,
            "ttl": record_ttl
        })
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.request("PUT", url, headers=headers, data=payload, auth=(c.USERNAME, c.PASSWORD))

        if response.status_code == 200:
            print(f"{datetime.now()} :: NOTICE: Record successfully updated.")
            self.previous_ip = str(self.current_ip)
            return True
        else:
            print(f"{datetime.now()} :: ERROR: Record not updated.  Received non-200 status code from API.")
            return False
        

    def get_dns_record_id(self) -> dict:
        """
        Returns a dictionary with the current dns record settings.
        
        Example:
        {
            "id": 190615683,
            "domainName": "example.org",
            "host": "test",
            "fqdn": "test.example.org.",
            "type": "A",
            "answer": "100.64.0.1",
            "ttl": 300
        }
        """
        url = f"{self.name_api_url}domains/{self.domain}/records?perPage=1000"
        response = requests.request("GET", url, auth=(c.USERNAME, c.PASSWORD))
        if response.status_code != 200:
            print(f"{datetime.now()} :: ERROR: Name.com not available.  Reason: {response.reason} :: {response.text}")
            return None
        records = json.loads(response.text)["records"]
        for record in records:
            # str().rstrip is needed since fqdn can sometimes be returned from API with a period at the end.
            if record["fqdn"].rstrip(".") == self.fqdn and record["type"] == self.dns_record_type:
                return record
        else:
            print(f"{datetime.now()} :: ERROR: Record not found on name.com with fqdn='{self.fqdn}' and type='{self.dns_record_type}'.")
            return None
    

    def find_nth(self, haystack, needle, n):
        """
        Finds index of the *n*'th occurrence of *needle* within *haystack*.     
        
        Returns -1 when the *n*'th occurrence is not found.
        """
        start = haystack.find(needle)
        while start >= 0 and n > 1:
            start = haystack.find(needle, start+len(needle))
            n -= 1
        return start

def main():
    dns_object = Record_Updater()
    # If we're running forever, set the updater in a loop.
    while c.RUN_FOREVER is True:
        dns_object.dns_updater()
        time.sleep(60*c.RUN_INTERVAL)
    else:
        dns_object.dns_updater()


if __name__ == "__main__":
    main()
