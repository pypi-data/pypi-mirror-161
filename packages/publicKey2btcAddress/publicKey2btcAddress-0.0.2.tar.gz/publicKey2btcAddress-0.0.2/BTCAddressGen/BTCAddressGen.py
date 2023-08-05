from bit import  format
class BTCAddressGen:
    def __init__(self,storemangroup,net = 'main'):
        '''
        :param storemangroup:
                     {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "result": {
                            "groupId": "0x000000000000000000000000000000000000000000000041726965735f303034",
                            "status": "5",
                            "deposit": "14977548978465740700066756",
                            "depositWeight": "17991035478465740700066756",
                            "selectedCount": "21",
                            "memberCount": "22",
                            "whiteCount": "1",
                            "whiteCountAll": "11",
                            "startTime": "1615262400",
                            "endTime": "1617940800",
                            "registerTime": "1614569510",
                            "registerDuration": "520098",
                            "memberCountDesign": "21",
                            "threshold": "15",
                            "chain1": "2153201998",
                            "chain2": "2147483708",
                            "curve1": "1",
                            "curve2": "0",
                            "tickedCount": "0",
                            "minStakeIn": "10000000000000000000000",
                            "minDelegateIn": "100000000000000000000",
                            "minPartIn": "10000000000000000000000",
                            "crossIncoming": "30000000000000000000",
                            "gpk1": "0x0c440bf2b594bdf526cbbcaae75dcb5f93d1f9bdd2f234f853fe4acf5f0e2d6d0525ad07f29f86943bc7c356a80e08e7345b12bc9bf5eb10e9d787b478f5ebb3",
                            "gpk2": "0x273c3273c072f826f728f865d58ccd297b293b87045fd806973d2a4d82f220a072bc5240c7d5920e0ddfdb0e01aeba184de9ef8ae14f5748243d8fa58d28e136",
                            "delegateFee": "1000"
                        }
                    }
        :return:
        '''
        self.net = net
        self.storemangroup = storemangroup
        self.type = \
            {
            "BTC":{"test":b'\x6f',"main": b'\x00'},
            "LTC":{'test':b'\x6f',"main": b'\x30'},
            "DOGE":{"test":b'q',"main": b'\x1e'}
            }
        if storemangroup['result']['curve1'] == 0:
            gpk = storemangroup['result']['gpk1']
        else:
            gpk = storemangroup['result']['gpk2']

        self.public_key_hex = '04' + gpk[2::]

    def Public_key_to_address(self, chain):
        '''
        :return:
        '''

        public_key = bytes.fromhex(self.public_key_hex)
        version = self.type[chain][self.net]

        length = len(public_key)

        if length not in (33, 65):
            raise ValueError('{} is an invalid length for a public key.'.format(length))
        return format.b58encode_check(version + format.ripemd160_sha256(public_key))

if __name__ == '__main__':
    gr =     {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "groupId": "0x000000000000000000000000000000000000000000000000006465765f303232",
            "status": "5",
            "deposit": "307199999999999999953800",
            "depositWeight": "435649999999999999930700",
            "selectedCount": "25",
            "memberCount": "25",
            "whiteCount": "1",
            "whiteCountAll": "11",
            "startTime": "1623211200",
            "endTime": "1623816000",
            "registerTime": "1623121135",
            "registerDuration": "10875",
            "memberCountDesign": "25",
            "threshold": "17",
            "chain1": "2153201998",
            "chain2": "2147483708",
            "curve1": "1",
            "curve2": "0",
            "tickedCount": "0",
            "minStakeIn": "10000000000000000000000",
            "minDelegateIn": "100000000000000000000",
            "minPartIn": "10000000000000000000000",
            "crossIncoming": "0",
            "gpk1": "0x10b3eb33a8b430561bb38404444c587e47247205771a40969ceabe0c08423ab220b5ddf25f856b71f6bb54cea88bceaa1bbe917f5d903ff82691a345ea4e0556",
            "gpk2": "0xca8ef3a93b2819851e3587dc0906a7e6563ab55ab4f8de76077813df03becc21a9a10957256667fbe3bca2aecd2db0ae5d76b8e8a636dc61e1b960a32b105bdb",
            "delegateFee": "1000"
        }
    }
    btc = BTCAddressGen(gr,'test')
    print(btc.Public_key_to_address('LTC'))
    print(btc.Public_key_to_address('BTC'))
    print(btc.Public_key_to_address('DOGE'))
