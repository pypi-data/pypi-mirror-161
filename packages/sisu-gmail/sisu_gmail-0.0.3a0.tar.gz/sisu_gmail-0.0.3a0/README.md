# sisu_gmail - abstractions of the Gmail API

Running the tests:

1) If this is your first test, make an **unused gmail address**.

2) Make sure to delete any welcome emails, etc.

3) git clone https://github.com/loren-magnuson/sisu_gmail && cd sisu_gmail
 
4) Put your Gmail API enabled credentials JSON in credentials.json.

5) python -m unittest

6) The Gmail API auth flow should start, complete it.

7) The auth token for your test email will be saved as token.json.

8) Tests should now attempt to complete.

9) Before your next test run, delete any leftover emails.
