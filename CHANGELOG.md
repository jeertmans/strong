# Changelog


### 0.2.2

* Type checking is more reliable, more scalable but cannot see inside containers
* Command line tool is still in WIP

#### Major changes

* changing order of parameters in `check_obj_typing`
* way of type-checking is changed
* type of variable inside containers are not verified anymore (e.g.: `list` is will provide the same results as `list[int]`)
