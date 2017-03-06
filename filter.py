"""
This example shows how to send a reply from the proxy immediately
without sending any data to the remote server.
"""
from mitmproxy import http
from mitmproxy import flowfilter
from mitmproxy import ctx             # log facility


class Filter:
	def __init__(self, spec):
		self.filter = flowfilter.parse(spec)

	def response(self, flow):
		if flowfilter.match(self.filter, flow):
			print("Flow matches filter:")
			print(flow)

	def request(self, flow):
		# pretty_url takes the "Host" header of the request into account, which
		# is useful in transparent mode where we usually only have the IP otherwise.

		print("Request")	
		if flow.request.pretty_url == "http://latribune.fr/":
			flow.response = http.HTTPResponse.make(
		    		200,  # (optional) status code
		    		b"Hello World",  # (optional) content
		    		{"Content-Type": "text/html"}  # (optional) headers
			)

def start():
	# Lists:  http://dsi.ut-capitole.fr/blacklists/download/blacklists.tar.gz
	ctx.log.info("This is some informative text.")
	filters = "~u latribune.fr"
	for i in range(0,2500):
		filters = " ~u test" + str(i) + " | " + filters
	for i in range(0,2500):
		filters = " ~bs test" + str(i) + " | " + filters
	# return Filter("~u latribune.fr")
	print("Compiling regexp")
	flowfilter.match("aaa", filters)
	print("Regexp compiled")
	ctx.log.error("This is an error.")
	return Filter(filters)
