import replier_lib as replier
import connector_lib as connector


response = replier.UnstructuredReplyToBroker('{ "value" :' + str(20) +' }')
response2 = replier.SemistructuredReplyToBroker("20", '{"value" : %%TOREPLACE%% }')
response3 = replier.ReplyToBroker("20")


msg = '{"timestamp":"2022-06-17T09:58:34.152716","Host":"10.0.2.15:8061","User-Agent":"orion/3.6.0 libcurl/7.61.1","Fiware-Servicepath":"/","Accept":"application/json","Content-Length":"260","Content-Type":"application/json; charset=utf-8","Fiware-Correlator":"49330d2c-ee13-11ec-be47-0242ac130002; cbnotif=1","Ngsiv2-AttrsFormat":"normalized","Body":{"subscriptionId":"62a8907ec8eef3395b17eafd","data":[{"id":"urn:ngsi-ld:Product:010","type":"Product","name":{"type":"Text","value":"Lemonade","metadata":{}},"price":{"type":"Number","value":20,"metadata":{}},"size":{"type":"Text","value":"S","metadata":{}}}]}}'
elem = connector.Parse(msg)


ld_msg = '{"timestamp":"2022-06-17T10:03:15.040031","Host":"10.0.2.15:8061","User-Agent":"orion/1.15.0-next libcurl/7.52.1","Fiware-Service":"orion","Fiware-Servicepath":"/","Accept":"application/json","Content-Length":"611","Content-Type":"application/json; charset=utf-8","Ngsiv2-AttrsFormat":"normalized","Link":"<https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld>; rel=\'http://www.w3.org/ns/json-ld#context\'; type=\'application/ld+json\'","Body":{"id":"urn:ngsi-ld:Notification:62ac35431abfb7df7ab7f5bc","type":"Notification","subscriptionId":"urn:ngsi-ld:Subscription:62ac352f1abfb7df7ab7f5bb","notifiedAt":"2022-06-17T08:03:15.037Z","data":[{"id":"urn:ngsi-ld:Building:store001","type":"Building","address":{"type":"Property","value":{"streetAddress":"Bornholmer Straffe 65","addressRegion":"Berlin","addressLocality":"Prenzlauer Berg","postalCode":"10439"}},"category":{"type":"Property","value":"Prova"},"name":{"type":"Property","value":"Bosebrucke Einkauf"},"location":{"type":"GeoProperty","value":{"type":"Point","coordinates":[13.3986,52.5547]}}}]}}'
ld_elem = connector.Parse(ld_msg)
