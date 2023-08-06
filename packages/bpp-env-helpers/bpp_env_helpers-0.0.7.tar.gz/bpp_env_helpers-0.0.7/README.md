# environment-helpers

package for generalizing qa project setup


### Making Queries
- function to read query file
```
def get_query_string(path_to_query_file) -> str:
    # implementation
```
- function to send the request with parameters
```
def make_query(gql_url, query_string, query_file_path, variables) -> Response:
    # implementation
```

### Validating parameters for test runs (WIP)
#### Required Parameters
- faculty-admin-portal
  - env = tst|stgapp
  - browser = chromium|firefox|webkit
- faculty-portal
  - env = tst|stgapp
  - browser = chromium|firefox|webkit
- qbank-student-portal
  - env = tst|stgapp
  - browser = chromium|firefox|webkit
- qbank-admin-portal
  - env = tst|stgapp
  - browser = chromium|firefox|webkit
- cf-student-portal
  - env = tst|stgapp|beta
  - browser = chrome
- cf-admin-portal
  - env = tst|stgapp|beta
  - browser = chrome
- mcat/lsat-admin-portal
  - env = tst|stgapp
  - browser = chrome
  - course = mcat|lsat
- mcat-student-portal
  - env = tst|stgapp|beta|prod
  - browser = chrome
- lsat-student-portal
  - env = tst|stgapp|beta|prod
  - browser = chrome
- rev-tech
  - env = tst|stgapp
  - browser = chrome

#### Booleans to Set Up
check if there's user/password, if so, tell the run to log in with that data
- create a boolean called `log_in_with_cookie = False` 

### Reading and returning environment data (WIP)

### Reading and returning account data (WIP)

### Triggering functions (WIP)

### Properties (maybe) (WIP)

### Resetting (maybe) (WIP)
