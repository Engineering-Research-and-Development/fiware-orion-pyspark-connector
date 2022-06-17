import replier_lib as replier


response = replier.UnstructuredReplyToBroker('{ "value" :' + str(20) +' }')
response2 = replier.SemistructuredReplyToBroker("20", '{"value" : %%TOREPLACE%% }')
response3 = replier.ReplyToBroker("20")
