import requests
import json
from ast import literal_eval
from time import sleep


def rebuildHost(node, server, user='admin', password='admin'):
  auth=(user,password)
  headers = {'Content-Type': 'application/json', }
  url= 'http://' + server + '/api/v2/'
  data=json.dumps({'host': {'build': 'true'}})
  r = requests.put(url + 'hosts/%s' % node, data=data, headers=headers, auth=auth)
  if r.status_code != requests.codes.ok:
    print 'Failure to build %s' % node
    return r.status_code
  data=json.dumps({'device': 'pxe'})
  r = requests.put(url + 'hosts/%s/boot' % node, data=data, headers=headers, auth=auth)
  if r.status_code != requests.codes.ok:
    print 'Failure to set boot to PXE for node %s' % node
    return r.status_code

  reloaded=0
  
  while reloaded <= 5:
    data=json.dumps({'power_action': 'status'})
    r = requests.put(url + 'hosts/%s/power' % node, data=data, headers=headers, auth=auth)
    if r.status_code != requests.codes.ok:
      print 'Unable to get power status for node %s' % node
      return r.status_code
    result= str(r.text)
    result= literal_eval(result)
    if result['power'] == 'on':
      if reloaded:
	print 'Power is back on after reboot'
        break
      else:
        print 'Power is on, rebooting...'
        data=json.dumps({'power_action': 'reboot'})
        r = requests.put(url + 'hosts/%s/power' % node, data=data, headers=headers, auth=auth)
    elif result['power'] == 'off':
      data=json.dumps({'power_action': 'start'})
      r = requests.put(url + 'hosts/%s/power' % node, data=data, headers=headers, auth=auth)
    else:
      raise RuntimeError('Unable to detect state of node')
      return 0
    reloaded+=1
    sleep(10)

  if r.status_code != requests.codes.ok or reloaded > 5:
    print 'Rebuild Failed with status code %s after %d tries' % (r.status_code, reloaded)
    return 0
  else:
    print 'Rebuiding...'
    return 1
     
  

if __name__ == '__main__':
  print rebuildHost(node='d28vl02.redhat.com', user='admin', password='odlrocks', server='10.6.65.1')

