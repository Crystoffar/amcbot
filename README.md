# AMCBot
 
This is a discord bot, built using discord.py that is meant to track values for AMC crew screenings
by using SQLite3. The rules of screenings is as follows.

1. Crew members who go to a crew screening should use to !attend command to gain 1 entry into the raffle for choosing the movie for the next screening. If the member already has an entry they will gain an additional entry. If the crew member chose the movie for a screening within the last 3 screenings, they are on cooldown and will not be able to gain an entry. Crew members can check how many entries/how many more screenings they will by using the !check command.

2. After the screening is over and all crew members have recorded their attendance, the administrator will use the !raffle to conduct the raffle. The crew member who wins the raffle will choose the next film, their entries will be set to 0 and they will be put on cooldown for 3 screenings. Any crew members on cooldown will have their cooldown reduced by 1.

3. For any other screenings that occur that are not chosen by crew members. The administrator can use the !decCD command to reduce cooldowns by 1.
