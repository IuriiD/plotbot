# 'PlotBot' / Chatbot for charting

<p>
    <b>Try this chatbot in</b>
    <br>- <a href="http://t.me/MakeMyChartBot" target="_blank"><b>Telegram</b></a> and
    <br>- <a href="https://bot.dialogflow.com/plotbot" target="_blank"><b>Web Demo</b></a> (text-only chat).
    <br>A version for <a href="https://www.google.com/url?q=https%3A%2F%2Fwww.facebook.com%2Fmessages%2Ft%2FChartingBot&sa=D&sntz=1&usg=AFQjCNEse1j0mozD-y9gSGg1DQ8fDVF4_w" target="_blank">Facebook Messenger</a> (here's the <a href="https://www.google.com/url?q=https%3A%2F%2Fwww.facebook.com%2FChartingBot%2F&sa=D&sntz=1&usg=AFQjCNHqwFZYSyQUw0C6HvzEsIxvqV5fDQ" target="_blank">bot page</a>) (very similar to the one in Telegram) is also available but not public yet (waiting for approval; in case anybody is interested I can add you to testers on FB).
</p>
<p>
    Here’s how it looks in Telegram and Web Demo:
    <a href="https://iuriid.github.io/img/pb-4.gif" target="_blank"><img src="https://iuriid.github.io/img/pb-4.gif" class="img-fluid img-thumbnail" style="max-width: 800px"></a>
    <br>
    And here’s the version for Facebook Messenger:
    <a href="https://iuriid.github.io/img/pb-5.gif" target="_blank"><img src="https://iuriid.github.io/img/pb-5.gif" class="img-fluid img-thumbnail" style="max-width: 800px"></a>
</p>
<p>
    <b>General info</b>
    <br>This chatbot was build for learning purposes/proof of concept, without specific practical assignment, and is open source (including Dialogflow’s part - see <a href="https://github.com/IuriiD/plotbot/blob/master/PlotBot.zip" target="_blank">PlotBot.zip</a>).
    <br>PlotBot can build bar, line, pie charts (each in several subtypes like basic/horizontal/stacked for bar and line charts and basic/”donut”/half-pie in case of pie charts), and also scatter diagrams. Webhooks are written on Python. <a href="http://www.google.com/url?q=http%3A%2F%2Fpygal.org%2Fen%2Fstable%2Findex.html&sa=D&sntz=1&usg=AFQjCNEjQ5WyKQh-OxLm3g_YkRPX09rFKg" target="_blank">Pygal</a> python library is used for charting. Charts are presented as png and svg (interactive) images. I'm hosting my webhooks on a server with Ubuntu and nginx, which is working on a virtual machine in Google Cloud.
</p>
<p>
    <b>Structure</b>
    <br>Intents structure for PlotBot is as follows (a big image 5k pixels width ;):
    <a href="https://iuriid.github.io/img/plotbot_intents_structure.gif" target="_blank"><img src="https://iuriid.github.io/img/plotbot_intents_structure.gif" class="img-fluid img-thumbnail" style="max-width: 800px"></a>
    A stepwise “slot-filling” dialog is assumed where user is suggested to name a chart, choose chart type, chart subtype, then to enter one or several data series and then to confirm chart building. Two webhooks are used for each chart type – one to validate data series and another to build and present charts.
    <br>These scheme seems to be rather redundant and already now, after building my 2nd chatbot I would have shortened it to 1 block instead of 4 with using more webhooks.
    <br>Entities (chart types and subtypes/styles) - quite simple:
    <a href="https://iuriid.github.io/img/pb-6.gif" target="_blank"><img src="https://iuriid.github.io/img/pb-6.gif" class="img-fluid img-thumbnail" style="max-width: 800px"></a>
    For a more detailed view please see the chatbot agent and source code for webhooks.
</p>
<p>
    <b>Possible further improvements</b>
    <br>If desired,
    <br>- PlotBot can be restructured from current rigid “slot-filling” style when it successively defines chart name >> chart type >> chart subtype >> data series to a more intelligent one, for example, to understand complex user-initiated inputs like “build bar chart for data 10, 20, 30, 40”;
    <br>- as I’ve mentioned the structure of the bot probably can be simplified on the Dialogflow’s side by using more webhooks;
    <br>- in addition to the 4 chart types that PlotBot can already build other chart types can be added. Also another charting library or service can be used instead of Pygal (for example, I thought about DASH).
    <br>- porting to other platforms (besides Telegram and FB),
    <br>but I decided to stop with this bot where it is and proceed to my other ideas/topics to learn.
</p>
