# Passwords Package

A package to interface with the Passwordstate API to retrieve passwords.

## Setup
Install dependencies in requirements.txt

Initialize an object with the api base url and the api key:
- api_base_url (str): the base url of the Passwordstate api
- api_key (str): the api secret key

```python
api_base_url = "https://passwords.mydomain.com"
api_key = "123mykey789"
pw_lookup = passwords.PasswordstateLookup(
    api_base_url,
    api_key
)
```

## Usage
Use the object's methods to find passwords. eg:
```python
pw_lookup.get_pw_by_title(5678, "my_password_title")
# returns the password with the given title in the given password list, as a string
```
or
```python
pw_lookup.get_pw(1234)
# returns the password with id 1234 as a string
```
or
```python
pw_lookup.get_pw_list(5678)
# returns a list of dictionaries including passwords for the password list with id 5678
```
