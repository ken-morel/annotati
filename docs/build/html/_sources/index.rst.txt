.. annotati documentation master file, created by
   sphinx-quickstart on Sun Nov 12 21:35:08 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Welcome to annotati's documentation!
==================================================

.. toctree::
   :maxdepth: 2
   :glob:
   :numbered:
   :caption: Contents:

   *
   methods/*

==================================================
Intro
==================================================
   annotati is a python package which helps you create function overloads and annotation typechecking as just adding a decorator

--------------------------------------------------
`annotati.annotati() <annotati.html>`_
--------------------------------------------------

permits you to typecheck arguments for annotations on function call

.. code-block:: python

   from annotati import annotati
   @annotati()
   def sum(a:int, b:int) -> int:
   """def sum(a:int, b:int) -> int:
   sums two integers
   :param a: integer 1
   :param b: integer 2

   :returns: the sum of a and b
   """
      return a + b


--------------------------------------------------
`annotati.overload() <overload.html>`_
--------------------------------------------------

permits you to create function overloads


>>> from annotati import overload
>>> @overload()
... def devide(a:int|float, b:0) -> None: # division by zero
...    raise ZeroDivisionError(f"deviding {a} by {b}")
...
>>> @overload()
... def devide(a:int|float, b:int|float) -> int|float:  # a and b are *int* or *float*
...    return a / b
...
>>> @overload()
... def devide(a:str, b:str) -> str: # a and b are both *str*
...    a, b = float(a), float(b) # convert to *float*
...    quotient = a / b # find quotient
...    return str(quotient) # convert to *str* and return
...
>>> devide(1, 2)
0.5
>>> devide("1", "2")
'0.5'
>>> devide(1, 0)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\pymodules\annotati\__init__.py", line 89, in call
    return oload(*args, **kw)
           ^^^^^^^^^^^^^^^^^^
  File "<stdin>", line 3, in devide
ZeroDivisionError: deviding 1 by 0









Indices and tables
==================================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
