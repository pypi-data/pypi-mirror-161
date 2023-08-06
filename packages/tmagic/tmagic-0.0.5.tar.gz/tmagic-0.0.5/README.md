# README

IPython custom cell magic to test code snippets typed into notebook cells.

## Installation

This package depends on IPython, you may need to install it first.

### Install from PyPI

As of 2022-07-01, `tmagic` is available at `https://pypi.org/project/tmagic/`.
Install it as usual: `pip3 install tmagic`.

### Install from BitBucket

To install the package for yourself as user:

`pip install git+ssh://git@bitbucket.org/interquadrat/testmagic.git`

You will need to have the appropriate credentials to get this working.

### Install from a local repository

To get around BitBucket authentication issues, the trick is to install
from the _local_ Git repository.

Assuming that this local repo belongs to the user "teacher" that also has `sudo` rights,
then install the package for all users like this:

`sudo -H pip3 install git+file:///home/teacher/PROJECTS/training/testmagic`

where you may need to modify the path to the local repo.

## How to use

See also the example IPython notebook file `example.ipynb`.
The description below explains usage in a bit more detail.

### Preparation

Import the `TestMagic` class and create an instance of it that is connected to the harness.

```
from tmagic import TestMagic
magic = TestMagic()
magic.register_test("answer", 42)
```

### Usage examples

Start a cell with `%%testexpr <testname>` where `<testname>` is the name of the test
that you registered with the Harness object (`"answer"` in the above example).
Then add one or more Python statements to the cell. 
The last statement must evaluate to the "good value" (`42`) defined in the `register_test`
method invocation.

The following test will fail:

```
%%testexpr answer
a = 6
b = 8
a*b
```

When executing this cell, the output will be:

```
Test failed :-(
48
```

This, however, will succeed:

```
%%testexpr answer
a = 6
b = 7
a*b
```

producing the output:

```
Test passed :-)
42
```

### Register several tests at once

The `register_tests()` convenience method lets you register several test name - expected value pairs.

```
tests = { "square":4, "cube":8 }
magic.register_tests(tests)
```

Run the tests (both will succeed of course):

```
%%testexpr square
2*2
```

```
%%testexpr cube
pow(2,3)
```
