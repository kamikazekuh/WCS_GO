"D:\steamcmd\steamapps\common\Counter-Strike Global Offensive Beta - Dedicated Server\csgo\addons\source-python\plugins\wcs\resources\events"
{
    "wcs_changerace"
    {
        "userid"	"short"	// The userid of the player involved in the event.
        "oldrace"	"string"	// The old race of the user.
        "newrace"	"string"	// The new race of the user.
    }
    "wcs_gainxp"
    {
        "userid"	"short"	// The userid of the player involved in the event.
        "amount"	"short"	// Amount of xp.
        "levels"	"short"	// Amount of Levels.
        "currentxp"	"short"	// Current XP.
        "reason"	"string"	// reason for xp gain.
    }
    "wcs_levelup"
    {
        "userid"	"short"	// The userid of the player involved in the event.
        "race"	"string"	// Race on level up.
        "oldlevel"	"short"	// oldlevel
        "newlevel"	"short"	// newlevel
        "amount"	"short"	// Amount of levels.
    }
    "wcs_itembought"
    {
        "userid"	"short"	// The userid of the player involved in the event.
        "item"	"string"	// Item that was bought
        "cost"	"short"	// Cost of the item
    }
    "wcs_player_spawn"
    {
        "userid"	"short"	// The userid of the player involved in the event.
    }
}
