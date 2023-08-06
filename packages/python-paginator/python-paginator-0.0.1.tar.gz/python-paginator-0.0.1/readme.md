## Example of usage:

```python
from paginator import core

object_list = [obj_1, obj_2, obj_n...]

paginator = core.paginate(object_list, page_limit=50, start_page=0)
```

**Get current page response:**
```python
paginator.response
```

**When calling *next* or *previous* page you can access new page data with ```paginator.response```**

**Get next page:**
```python
paginator.get_next()
```

**Get previous page:**
```python
paginator.get_previous()
```

**Get response of requested page number:**
```python
paginator.get_page_response(page_number=0)
```

**Total pages:**

```python
paginator.total_pages
```

**Count objects:**
```python
paginator.total
```

**Iterating over paginator pages**

```python
for page in paginator:
...
```
