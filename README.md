# CS50 Finance
#### Intialization:
• Firstly, Click on the **drop-down** menu of ***Code*** button (in green color) and then click on **Download ZIP**. <br/>
• Secondly, Unzip it and log into **code.cs50.io** and Upload this directory named "Finance". <br/>
• We’ll need to register for an ***API key*** in order to be able to query IEX’s data. To do so, follow these steps:<br/>
1) Visit iexcloud.io/cloud-login#/register/.<br/>
2) Select the “Individual” account type, then enter your name, email address, and a password, and click “Create account”.<br/>
3) Once registered, scroll down to “Get started for free” and click “Select Start plan” to choose the free plan.<br/>
4) Once you’ve confirmed your account via a confirmation email, visit https://iexcloud.io/console/tokens.<br/>
5) Copy the key that appears under the Token column (it should begin with pk_).<br/>
##
• ***Now, In your terminal window, execute:***
$ export API_KEY=value<br/>
where *value* is that (copied) api_key,So paste the copied api_key inplace of *value*(in command) without any space immediately before or after the *=*. You also may wish to paste that value in a text document somewhere, in case you need it again later.<br/>
• And now, after the executing the above command you can finally execute ***flask run*** (within finance/) & Now click on the link generated which will takes you to *web app*
#### Description:
• In this project, I have built a ***web app*** (with assistance of David sir during my CS50x Course) which allows users to Login/Logout along with there passwords. And incase of wrong password user will redirect to *error page*.<br/>
• C$50 Finance, a web app via which you can manage portfolios of stocks. Not only will this tool allow you to check real stocks’ actual prices and portfolios’ values, it will also let you buy and sell stocks by querying IEX for stocks’ prices.<br/>
• I have added another functionality that allows users to ***change their passwords***.<br/>
• To see the current price of any stock, simply go to the **Quote** Tab and enter the stock symbol and hit enter. Current Price of that stock will be displayed.<br/>
• Now, you can **Buy** the stocks as much as your cash allows and in case of ***insufficent balance*** you will get an ***error***<br/>
• And in the case of **Sell**, user can sell the stocks that he has purchased by selecting from the drop-down list. And if the user trys to sell more stocks than the purchased one, you will get an ***error***<br/>
• At last, In the **History** tab user can see history of all the stocks bought or sold at what price. Where **-** (negative) shares are use to represent ***sold***.
