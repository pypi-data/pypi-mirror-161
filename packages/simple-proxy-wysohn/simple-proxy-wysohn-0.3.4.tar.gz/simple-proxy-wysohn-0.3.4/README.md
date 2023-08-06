# simple_proxy
Use cycling proxies without the boilerplate codes

## Requests session
It directly uses the Session interface provided by the well known package, requests, so it's easy to adapt it by simply providing the session to your existing project.

## Use the proxy with the high response and low failure rate
Proxy automatically 'cycles' for the list of proxy servers provided you, yet it will try to keep the dead/slow proxy out of the process as much as possible.

# Installation
`pip install simple-proxy-wysohn`

# Usage

## Build the proxy dictionary
This is where you can set the destination of the file that has the list of the proxy. Each file should be named either http.txt, https.txt, socks4.txt, or socks5.txt and placed under the folder named `proxies`. As you may already noticed, each file will contain the list of proxies of the type specified by the text files' name, and each line is formatted as <ip>:<port>
  
  Ex: http.txt
  ```
  1.2.3.4:3333
  44.33.22.11:3334
  ```

  Following code will load all the text files automatically from the 'proxies' folder
  ```
  from simple_proxy2.pool.tools import build_proxy_dict

  proxy_dict = build_proxy_dict()
  ```

  You may change the target folder name
  ```
  from simple_proxy2.pool.tools import build_proxy_dict

  proxy_dict = build_proxy_dict('targetFolder')
  ```

  Or, simply create your own dictionary
  ```
  from simple_proxy2.pool.tools import build_proxy_dict

  proxy_dict = build_proxy_dict({'http': [
    '1.2.3.4:3344',
    '4.3.2.1:2234',
  ]})
  ```


## Set up the ProxyManager
Create a ProxyManager by providing the dictionary you have created above.
  
  - `test_url` will be used to 'test' each proxy periodically to see if the proxy is available and has a reliable connection.
  
  ```
  from requests import Session
  from simple_proxy2.proxy_manager import ProxyManager

  def simple_request(session: Session, a):
      print(a)
      return session, session.get(test_url, timeout=5)


  def process_callback(session, response):
      print(session, response.status_code)


  with ProxyManager(test_url, proxy_dict) as manager:
      for i in range(100): # note that each proxy_session() call will try different proxies when needed
          manager.proxy_session(simple_request, process_callback, args=(i,))
  ```

### Use it as Session
manager.proxy_as_request_session() will return the Session, which is directly backed by the ProxyManager. You can use it as the usual `requests`'s session, yet the only difference is that each call will use different proxy as needed.
  
  ```
  with ProxyManager(test_url, proxy_dict) as manager:
    session = manager.proxy_as_request_session()
    r = session.get('https://abc.com/bb')
    print(r.status_code)
  ```
  
 Note that setting the proxies parameter will be ignored in any case (that's pretty obvious since you don't need to use ProxyManager if you want to manually set the proxy)
  
### If you want to manually control the callback
You can provide `wait=True` argument to the proxy_session(), then it will return the whatever value returned by the function (simple_request in the example) when the request is successfully handled.
  
  ```
  with ProxyManager(test_url, proxy_dict) as manager:
    for i in range(100): # note that each proxy_session() call will try different proxies when needed
        manager.proxy_session(simple_request, process_callback, args=(i,), wait=True)
  ```

# Disclaimer
You are solely responsible to respect the policy of the website you are accessing and set appropriate connection limit. Any consequences casued by mis-using this package is not my responsibility.
