from pybitcoin import AddressFetcher

gAddress = AddressFetcher().generateGarlicAddress(True)
print(gAddress)