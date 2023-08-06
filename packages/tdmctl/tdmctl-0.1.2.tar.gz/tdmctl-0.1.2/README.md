# tdmctl Cli for management of TouDoum-Framework

## Sample of config file
```yaml
current_context: cluster1
context:
    cluster1: 
        host: localhost
        user: admin
        pass: admin
```
## .tdmctl folder structure
```yaml
.tdmctl:
  config.yml:
  modules:
    <context-name1>:
      <module-name1>:
        main.py:
    <context-name2>:
      <module-name1>:
        main.py:
      <module-name2>:
        main.py:
```