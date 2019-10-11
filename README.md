# movies-bot
A telegram bot that can recommend you movies based on genres, actors, or even other movies!

The bot was built in python. It was created integrating IBM-Watson with The Movie Database.

- Watson was used to make the bot understeand natural language. We use it to exctract intents from the user.
- After the intents are indetified, we use then to query on TMDB API (https://www.themoviedb.org/documentation/api).

- To run the bot you will need authentication keys for the TMDB API, Watson API, and telegram API.
- Send me an email (vssm@cin.ufpe.br) for the keys (We only have a small number of requests available for free so we couldn't make the keys public).
- After you get the keys, run the application in your local server with "python wat.py" (you might need to install some dependencies). After that, just go to telegram and send a message to the bot at @FilmaoBot.
