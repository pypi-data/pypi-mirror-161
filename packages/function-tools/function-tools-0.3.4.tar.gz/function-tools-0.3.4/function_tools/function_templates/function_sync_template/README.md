## Внедрение функции

```
   runner_manager = {{ camel_case_function_name }}RunnerManager()
   runner_manager.run()
   
   presented_result = {{ camel_case_function_name }}ResultPresenter(
      runnable_result=runner_manager.result,
   ).represent()
```
