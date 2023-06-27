# nso_live_status
This library is an example on how you can retrieve raw cli with Cisco NSO and parse the result with pyats/genie parser.

This is a generated Python package, made by:

  ncs-make-package --service-skeleton python-and-template \
                   --component-class main.Main nso-live-status-parser

It contains a dummy YANG model which implements a minimal Service
and an Action that doesn't really do anything useful. They are
there just to get you going.

You will also find two test cases in:

  test/internal/lux/service/
  test/internal/lux/action/

that you can run if you have the 'lux' testing tool.
Your top Makefile also need to implement some Make targets
as described in the Makefiles of the test cases.
You can also just read the corresponding run.lux tests and
do them manually if you wish.

The 'lux' test tool can be obtained from:

  https://github.com/hawk/lux.git
