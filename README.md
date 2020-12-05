# Pomodorro Timer

As Wikipedia says:

> The Pomodoro Technique is a time management method developed by Francesco Cirillo in the late 1980s. The technique uses a timer to break down work into intervals,    traditionally 25 minutes in length, separated by short breaks. Each interval is known as a pomodoro, from the Italian word for 'tomato', after the tomato-shaped kitchen timer that Cirillo used as a university student.

As a someone who learn a Python, it was very important for me to stay focused on the subject. This technique helped me, and I thought about making my own timer. And here it is.

## Main features

Yes, it's still a simple countdown timer. 

When setting up a timer, you can specify the type of action that you plan to perform during this time period, as well as select the tag that corresponds to this action. Data about the time spent usefully (**or not, it's up to you**) will be recorded in a json file.

In the Statistics section, you will see a graphs that illustrating data. Statistics are divided into three parts: a bar plot, a pie chart, and a table. The bar chart shows the number of minutes you spent per day, week, month, or year. When you hover over a rectangle, it turns red, and the number of minutes is displayed above it. 
The pie chart shows the percentage distribution of your minutes by the tags you selected before the launch. The table shows a list of your launches: the total number of minutes, the time interval, the task you spent your minutes on, and the corresponding tag.

You can change the button to start the timer and the sound that the timer make in the Settings section. Please note that the app can only play WAV format at this time. Unfortunately, GIF animation is also not supported.

## TODO:
* Try to implement minute tracking for any day, week, month or year, not just the current one.
* Add a features that help the app support gif animation and other sound formats

That's all for now. I'll be happy to have any comments regarding the code.