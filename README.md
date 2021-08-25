## World of Warships XVM (sort of)
**Installation**

 1. Clone this repository.
 2. Create a Python virtual environment in the clone repo directory and activate it.
 3. Install everything inside `requirements.txt` via pip
 
 **Running it**
 
 1. Copy everything inside the mod folder and paste it to `World_of_Warships\bin\XXXXXXX\res_mods`.
	 - You can find the right value for `XXXXXXX` in the file 
`World_of_Warships\game_info.xml`. Just look for the last 7 digit in `available` or `installed` attribute in `<version name="client" available="0.10.7.2.4365481" installed="0.10.7.2.4365481"/>`
 2. Run the script `xvm.py` on the activated Python environment.
	 ![enter image description here](https://cdn.discordapp.com/attachments/815060530829459539/880018838568181770/xvm.png)
 4. Run the game and enter a co-op or training battle to test it.
	- You should see something like this in the game:
	![xvm](https://cdn.discordapp.com/attachments/793654138880655362/877475891914096691/unknown.png)

**Footnotes**

 - If you don't know how to create a Python virtual environment, just look for tutorials online.
 - All PR calculation formula and ship expected values are provided by [wows-numbers](https://wows-numbers.com/personal/rating).
 - To Show/Hide the PR values, press the `HOME` button on your keyboard.
