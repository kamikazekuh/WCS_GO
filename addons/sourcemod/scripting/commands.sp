#include <sourcemod>
#include <sdktools>
#include <sdkhooks>
#include <console>
#include <cstrike>
#include <smlib>
#include <morecolors>
#define DMG_GENERIC			0
#define DMG_CRUSH			(1 << 0)
#define DMG_BULLET			(1 << 1)
#define DMG_SLASH			(1 << 2)
#define DMG_BURN			(1 << 3)
#define DMG_VEHICLE			(1 << 4)
#define DMG_FALL			(1 << 5)
#define DMG_BLAST			(1 << 6)
#define DMG_CLUB			(1 << 7)
#define DMG_SHOCK			(1 << 8)
#define DMG_SONIC			(1 << 9)
#define DMG_ENERGYBEAM			(1 << 10)
#define DMG_PREVENT_PHYSICS_FORCE	(1 << 11)
#define DMG_NEVERGIB			(1 << 12)
#define DMG_ALWAYSGIB			(1 << 13)
#define DMG_DROWN			(1 << 14)
#define DMG_TIMEBASED			(DMG_PARALYZE | DMG_NERVEGAS | DMG_POISON | DMG_RADIATION | DMG_DROWNRECOVER | DMG_ACID | DMG_SLOWBURN)
#define DMG_PARALYZE			(1 << 15)
#define DMG_NERVEGAS			(1 << 16)
#define DMG_POISON			(1 << 17)
#define DMG_RADIATION			(1 << 18)
#define DMG_DROWNRECOVER		(1 << 19)
#define DMG_ACID			(1 << 20)
#define DMG_SLOWBURN			(1 << 21)
#define DMG_REMOVENORAGDOLL		(1 << 22)
#define DMG_PHYSGUN			(1 << 23)
#define DMG_PLASMA			(1 << 24)
#define DMG_AIRBOAT			(1 << 25)
#define DMG_DISSOLVE			(1 << 26)
#define DMG_BLAST_SURFACE		(1 << 27)
#define DMG_DIRECT			(1 << 28)
#define DMG_BUCKSHOT			(1 << 29)
#define PLUGIN_VERSION "1.0.0.5"

#define TRACE_START 24.0
#define TRACE_END 64.0

#define TEAM_T 2
#define TEAM_CT 3

#define COLOR_T "255 0 0"
#define COLOR_CT "0 0 255"
#define COLOR_DEF "0 255 255"

#define MAX_LINE_LEN 256

new i_HasAnti[MAXPLAYERS+1];
new i_Chance[MAXPLAYERS+1];
new random;

new Handle:c_var = INVALID_HANDLE;
new Handle:trace = INVALID_HANDLE;

public OnPluginStart()
{
	RegServerCmd("wcs_give", GivePlayer);
	RegServerCmd("wcs_dealdamage", DoDamage);
	RegServerCmd("wcs_getwallbetween", GetWall_Register);
	RegServerCmd("wcs_getgravity", GravityGet);
	RegServerCmd("wcs_getgun", GunGet);
	RegServerCmd("wcs_getdistance", DistanceRegister);
	RegServerCmd("wcs_teleport", TeleportRegister);
	RegServerCmd("wcs_slap", SlapRegister);
	RegServerCmd("wcs_thirdperson", ThirdpersonRegister);
	RegServerCmd("wcs_getdeaths", GetDeathRegister);
	RegServerCmd("wcs_setdeaths", SetDeathRegister);
	RegServerCmd("wcs_getscore", GetScoreRegister);
	RegServerCmd("wcs_setscore", SetScoreRegister);
	RegServerCmd("wcs_shake", ShakeRegister);
	RegServerCmd("wcs_getsmadmin", AdminRegister);
	RegServerCmd("wcs_entitygethealth", EntityGetHealthRegister);
	RegServerCmd("wcs_entitysethealth", EntitySetHealthRegister);
	RegServerCmd("wcs_entitytakehealth", EntityTakeHealthRegister);
	RegServerCmd("wcs_create_prop", CreatePropRegister);
	RegServerCmd("wcs_evasion", EvasionRegister);
	RegServerCmd("wcs_steal", StealPlayer);
	RegServerCmd("wcs_leech", LeechPlayer);
	RegServerCmd("wcs_effect_prop", PropEffect);
	RegServerCmd("wcs_geteyecoords", EyeCoords);
	HookEvent("player_hurt", Event_PlayerHurt, EventHookMode_Pre);
	HookEvent("player_spawn", Event_PlayerSpawn);
}

public Action:EyeCoords(args)
{
	new String:userid[128];
	new String:var1[1024];
	new String:var2[1024];
	new String:var3[1024];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2,var1, sizeof(var1));
	GetCmdArg(3, var2, sizeof(var2));
	GetCmdArg(4, var3, sizeof(var3));
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	new Handle:variable1 = FindConVar(var1);
	new Handle:variable2 = FindConVar(var2);
	new Handle:variable3 = FindConVar(var3);
	new Float:posi[3];
	GetClientEyePosition(useridc, posi);
	SetConVarFloat(variable1, posi[0]);
	SetConVarFloat(variable2, posi[1]);
	SetConVarFloat(variable3, posi[2]);
}

public Action:PropEffect(args)
{
	new String:x1[1024];
	new String:y1[1024];
	new String:z1[1024];
	new String:propname[1024];
	new String:delay[128];
	GetCmdArg(1, x1, sizeof(x1));
	GetCmdArg(2, y1, sizeof(y1));
	GetCmdArg(3, z1, sizeof(z1));
	GetCmdArg(4, propname, sizeof(propname));
	GetCmdArg(5, delay, sizeof(delay));
	PrecacheModel(propname);
	decl Float:g_fOrigin[3]
	g_fOrigin[0] = StringToFloat(x1);
	g_fOrigin[1] = StringToFloat(y1);
	g_fOrigin[2] = StringToFloat(z1);
	new g_iEnt = CreateEntityByName("prop_dynamic");
	SetEntityModel(g_iEnt, propname);
	DispatchKeyValue(g_iEnt, "targetname", "Name");
	DispatchKeyValue(g_iEnt, "Solid", "6");
	DispatchSpawn(g_iEnt);
	TeleportEntity(g_iEnt, g_fOrigin, NULL_VECTOR, NULL_VECTOR);
	SetEntityMoveType(g_iEnt, MOVETYPE_VPHYSICS);
	SetEntProp(g_iEnt, Prop_Data, "m_CollisionGroup", 2);
	CreateTimer(StringToFloat(delay), Prop_Remove, g_iEnt);
	return Plugin_Handled;
}

public Action:Prop_Remove(Handle:timer, any:g_iEnt)
{
	Entity_SetHealth(g_iEnt, 0, true, true);
	CloseHandle(timer);
	timer = INVALID_HANDLE;
}

public Action:LeechPlayer(args)
{
	new String:userid[128];
	new String:amountmin[128];
	new String:amountmax[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, amountmin, sizeof(amountmin));
	GetCmdArg(3, amountmax, sizeof(amountmax));
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	random = GetRandomInt(StringToInt(amountmin), StringToInt(amountmax));
	new health = GetClientHealth(useridc);
	SetEntityHealth(useridc, (health +random))
}
	
public Action:StealPlayer(args)
{
	new String:userid[128];
	new String:attacker[128];
	new String:amount[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, attacker, sizeof(attacker));
	GetCmdArg(3, amount, sizeof(amount));
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	new attackeri = StringToInt(attacker);
	new attackerc = GetClientOfUserId(attackeri);
	new amounti = StringToInt(amount);
	new usermoney = GetEntProp(useridc, Prop_Send, "m_iAccount");
	if (usermoney < amounti)
	{
		SetEntProp(useridc, Prop_Send, "m_iAccount", 0);
		new attackermoney = GetEntProp(attackerc, Prop_Send, "m_iAccount");
		SetEntProp(attackerc, Prop_Send, "m_iAccount", (attackermoney + usermoney));
	}
	if (usermoney >= amounti)
	{
		SetEntProp(useridc, Prop_Send, "m_iAccount", (usermoney - amounti));
		new attackermoney = GetEntProp(attackerc, Prop_Send, "m_iAccount");
		SetEntProp(attackerc, Prop_Send, "m_iAccount", (attackermoney + amounti));
	}
}

public Event_PlayerSpawn(Handle:event,const String:name[],bool:dontBroadcast)
{
	new client = GetClientOfUserId(GetEventInt(event,"userid"));
	i_HasAnti[client] = 0;
	i_Chance[client] = 0;
}


public Action:EvasionRegister(args)
{
	new String:userid[128];
	new String:onoff[128];
	new String:chance[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, onoff, sizeof(onoff));
	GetCmdArg(3, chance, sizeof(chance));
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	i_HasAnti[useridc] = StringToInt(onoff);
	i_Chance[useridc] = StringToInt(chance);
}


public Action:Event_PlayerHurt(Handle:event, const String:name[], bool:dontBroadcast)
{
	new client = GetClientOfUserId(GetEventInt(event, "userid"));
	if (i_HasAnti[client] == 1)
	{
		random = GetRandomInt(0, 100);
		if(i_Chance[client] >= random)
		{
			new e_health = GetEventInt(event, "dmg_health");
			new c_health = GetClientHealth(client);
			SetEntityHealth(client, (c_health + e_health));
			CPrintToChat(client, "{green}[WCS] {lightgreen}Evasion - You've evaded an incoming attack");

		}
	}
}

public Action:EntityTakeHealthRegister(args)
{
	decl String:entity[64];
	decl String:value[64];
	GetCmdArg(1, entity, sizeof(entity));
	GetCmdArg(2, value, sizeof(value));
	Entity_TakeHealth(StringToInt(entity), StringToInt(value), true, true);
}

public Action:EntitySetHealthRegister(args)
{
	decl String:entity[64];
	decl String:value[64];
	GetCmdArg(1, entity, sizeof(entity));
	GetCmdArg(2, value, sizeof(value));
	Entity_SetHealth(StringToInt(entity), StringToInt(value), true, true);
}

public Action:EntityGetHealthRegister(args)
{
	new String:entity[128];
	new String:bvar[128];
	GetCmdArg(1, entity, sizeof(entity));
	GetCmdArg(2, bvar, sizeof(bvar));
	new health = Entity_GetHealth(StringToInt(entity));
	c_var = FindConVar(bvar);
	SetConVarInt(c_var, health);
}

public Action:AdminRegister(args)
{
	new String:userid[128];
	new String:bvar[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, bvar, sizeof(bvar));
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	new isadmin = Client_IsAdmin(useridc);
	c_var = FindConVar(bvar);
	SetConVarInt(c_var, isadmin);
}

public Action:ShakeRegister(args)
{
	new String:userid[128];
	new String:amplitude[128];
	new String:frequenzy[128];
	new String:duration[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, amplitude, sizeof(amplitude));
	GetCmdArg(3, frequenzy, sizeof(frequenzy));
	GetCmdArg(4, duration, sizeof(duration));
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	Client_Shake(useridc, SHAKE_START, StringToFloat(amplitude), StringToFloat(frequenzy), StringToFloat(duration));
}


public Action:SetScoreRegister(args)
{
	new String:userid[128];
	new String:value[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, value, sizeof(value));
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	Client_SetScore(useridc, StringToInt(value));
}

public Action:GetScoreRegister(args)
{
	new String:userid[128];
	new String:bvar[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, bvar, sizeof(bvar));
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	new score = Client_GetScore(useridc);
	c_var = FindConVar(bvar);
	SetConVarInt(c_var, score);
}

public Action:SetDeathRegister(args)
{
	new String:userid[128];
	new String:value[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, value, sizeof(value));
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	Client_SetDeaths(useridc, StringToInt(value));
}

public Action:GetDeathRegister(args)
{
	new String:userid[128];
	new String:bvar[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, bvar, sizeof(bvar));
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	new deaths = Client_GetDeaths(useridc);
	c_var = FindConVar(bvar);
	SetConVarInt(c_var, deaths);
}


public Action:ThirdpersonRegister(args)
{
	new String:userid[128];
	new String:value[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, value, sizeof(value));
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	if (StrEqual(value, "1", false))
	{
		Client_SetThirdPersonMode(useridc, true);
	}
	if (StrEqual(value, "0", false))
	{
		Client_SetThirdPersonMode(useridc, false);
	}
}

public Action:SlapRegister(args)
{
	new String:userid[128];
	new String:health[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, health, sizeof(health));
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	new healthi = StringToInt(health);
	SlapPlayer(useridc, healthi, false);
}

public Action:DistanceRegister(args)
{
	new String:bvar[128]
	new String:x1[128];
	new String:y1[128];
	new String:z1[128];
	new String:x2[128];
	new String:y2[128];
	new String:z2[128];
	GetCmdArg(1, bvar, sizeof(bvar));
	GetCmdArg(2, x1, sizeof(x1));
	GetCmdArg(3, y1, sizeof(y1));
	GetCmdArg(4, z1, sizeof(z1));
	GetCmdArg(5, x2, sizeof(x2));
	GetCmdArg(6, y2, sizeof(y2));
	GetCmdArg(7, z2, sizeof(z2));
	decl Float:vec1[3];
	decl Float:vec2[3];
	vec1[0] = StringToFloat(x1);
	vec1[1] = StringToFloat(y1);
	vec1[2] = StringToFloat(z1);
	vec2[0] = StringToFloat(x2);
	vec2[1] = StringToFloat(y2);
	vec2[2] = StringToFloat(z2);
	new Float:distance = GetVectorDistance(vec1, vec2, false);
	c_var = FindConVar(bvar);
	SetConVarFloat(c_var, distance);
}


public Action:GunGet(args)
{
	new String:userid[128];
	new String:bvar[128];
	new String:value[128];
	GetCmdArg(2, userid, sizeof(userid));
	GetCmdArg(1, bvar, sizeof(bvar));
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	GetClientWeapon(useridc, value, sizeof(value));
	c_var = FindConVar(bvar);
	SetConVarString(c_var, value);
}


public Action:GravityGet(args)
{
	new String:userid[128];
	new String:bvar[128];
	new Float:value;
	GetCmdArg(2, userid, sizeof(userid));
	GetCmdArg(1, bvar, sizeof(bvar));
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	value = GetEntityGravity(useridc)
	c_var = FindConVar(bvar);
	SetConVarFloat(c_var, value);
}

public Action:GivePlayer(args)
{
	new String:userid[128];
	new String:weapon[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, weapon, sizeof(weapon));

	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	if(IsPlayerAlive(useridc))
	{
		new String:currmap[128];
		GetCurrentMap(currmap, sizeof(currmap));
		if (StrEqual(currmap, "scoutzknivez_lwcs", false) == false)
		{
			GivePlayerItem(useridc, weapon);           
		}
		else
		{
			if (StrContains("weapon_scout;weapon_hegrenade;weapon_knife", weapon, false) != -1)
			{
				GivePlayerItem(useridc, weapon); 
			}
			else
			{
				CPrintToChat(useridc, "{GREEN}[WCS]: {YELLOW}This weapon is restricted on this map!")
			}
		}
		if (StrEqual(currmap, "aim_deagle7k", false) == false)
		{
			GivePlayerItem(useridc, weapon);           
		}
		else
		{
			if (StrContains("weapon_deagle;weapon_hegrenade;weapon_knife", weapon, false) != -1)
			{
				GivePlayerItem(useridc, weapon); 
			}
			else
			{
				CPrintToChat(useridc, "{GREEN}[WCS]: {YELLOW}This weapon is restricted on this map!")
			}
		}		
	}
	
	return Plugin_Handled;
}


public Action:DoDamage(args)
{
	new String:userid[128];
	new String:attacker[128];
	new String:damage[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, attacker, sizeof(attacker));
	GetCmdArg(3, damage, sizeof(damage));
	new useridi = StringToInt(userid);
	new attackeri = StringToInt(attacker);
	new useridc = GetClientOfUserId(useridi);
	new attackerc = GetClientOfUserId(attackeri);
	new damagei = StringToInt(damage);
	DealDamage(useridc, damagei, attackerc, DMG_BULLET, "");
	return Plugin_Handled;
}

DealDamage(victim,damage,attacker=0,dmg_type=DMG_GENERIC,String:weapon[]="")
{
	if(victim>0 && IsValidEdict(victim) && IsClientInGame(victim) && IsPlayerAlive(victim) && damage>0)
	{
		new String:dmg_str[16];
		IntToString(damage,dmg_str,16);
		new String:dmg_type_str[32];
		IntToString(dmg_type,dmg_type_str,32);
		new pointHurt=CreateEntityByName("point_hurt");
		if(pointHurt)
		{
			DispatchKeyValue(victim,"targetname","war3_hurtme");
			DispatchKeyValue(pointHurt,"DamageTarget","war3_hurtme");
			DispatchKeyValue(pointHurt,"Damage",dmg_str);
			DispatchKeyValue(pointHurt,"DamageType",dmg_type_str);
			if(!StrEqual(weapon,""))
			{
				DispatchKeyValue(pointHurt,"classname",weapon);
			}
			DispatchSpawn(pointHurt);
			AcceptEntityInput(pointHurt,"Hurt",(attacker>0)?attacker:-1);
			DispatchKeyValue(pointHurt,"classname","point_hurt");
			DispatchKeyValue(victim,"targetname","war3_donthurtme");
			RemoveEdict(pointHurt);
		}
	}
}


public Action:GetWall_Register(args)
{
	new String:bvar[128];
	new String:user1[128];
	new String:user2[128];
	GetCmdArg(1, bvar, sizeof(bvar));
	GetCmdArg(2, user1, sizeof(user1));
	GetCmdArg(3, user2, sizeof(user2));
	new user1_i = StringToInt(user1);
	new user1_c = GetClientOfUserId(user1_i);
	new user2_i = StringToInt(user2);
	new user2_c = GetClientOfUserId(user2_i);
	decl Float:clientOrigin[3];
	decl Float:entityOrigin[3];
	GetClientAbsOrigin(user1_c, clientOrigin);
	GetClientAbsOrigin(user2_c, entityOrigin);
	trace = TR_TraceRayFilterEx(clientOrigin, entityOrigin, MASK_SOLID, RayType_EndPoint, Filter_ClientSelf, user1_c);
	if(TR_DidHit(trace))
	{
		new ent = TR_GetEntityIndex(trace)
		if(ent != user2_c)
		{
			c_var = FindConVar(bvar);
			SetConVarString(c_var, "1");
		}
		else
		{
			c_var = FindConVar(bvar);
			SetConVarString(c_var, "0");
		}
	}
	return Plugin_Handled;
}

public bool:Filter_ClientSelf(entity, contentsMask, any:data)
{
	if(entity == data)
	{
		return false;
	}
	return true;
}

public Action:TeleportRegister(args)
{
	new String:userid[128];
	new String:x1[128];
	new String:x2[128];
	new String:x3[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, x1, sizeof(x1));
	GetCmdArg(3, x2, sizeof(x2));
	GetCmdArg(4, x3, sizeof(x3));
	new user_i = StringToInt(userid);
	new user_c = GetClientOfUserId(user_i);
	decl Float:go_vec[3];
	go_vec[0] = StringToFloat(x1);
	go_vec[1] = StringToFloat(x2);
	go_vec[2] = StringToFloat(x3);
	if(GetCollisionPoint(user_c, go_vec))
	{
		TeleportEntity(user_c, go_vec, NULL_VECTOR, NULL_VECTOR);
	}
}

stock bool:GetCollisionPoint(client, Float:pos[3], bool:eyes=true)
{
    decl Float:vOrigin[3], Float:vAngles[3], Float:vBackwards[3];
    new bool:failed = false;
    new loopLimit = 100;    // only check 100 times, as a precaution against runaway loops

    if (eyes)
    {
        GetClientEyePosition(client, vOrigin);
    }
    else
    {
        // if eyes is false, fall back to the AbsOrigin ( = feet)
        GetClientAbsOrigin(client, vOrigin);
    }
    
    GetClientEyeAngles(client, vAngles);
    GetAngleVectors(vAngles, vBackwards, NULL_VECTOR, NULL_VECTOR);
    NormalizeVector(vBackwards, vBackwards);
    ScaleVector(vBackwards, 10.0);    // TODO: percentage of distance from endpoint to eyes instead of fixed distance?
    
    trace = TR_TraceRayFilterEx(vOrigin, vAngles, MASK_SHOT, RayType_Infinite, TraceEntityFilterPlayer);
        
    if (TR_DidHit(trace))
    {    
        TR_GetEndPosition(pos, trace);
        //PrintToChat(client, "endpos %f %f %f", pos[0], pos[1], pos[2]);
        
        while (IsPlayerStuck(pos, client) && !failed)    // iteratively check if they would become stuck
        {
            SubtractVectors(pos, vBackwards, pos);        // if they would, subtract backwards from the position
            //PrintToChat(client, "endpos %f %f %f", pos[0], pos[1], pos[2]);
            if (GetVectorDistance(pos, vOrigin) < 10 || loopLimit-- < 1)
            {
                
                failed = true;    // If we get all the way back to the origin without colliding, we have failed
                //PrintToChat(client, "failed to find endpos");
                pos = vOrigin;    // Use the client position as a fallback
            }
        }
    }
    
    CloseHandle(trace);
    return !failed;        // If we have not failed, return true to let the caller know pos has teleport coordinates
}

#define BOUNDINGBOX_INFLATION_OFFSET 3

// Checks to see if a player would collide with MASK_SOLID (i.e. they would be stuck)
// Inflates player mins/maxs a little bit for better protection against sticking
// Thanks to andersso for the basis of this function
stock bool:IsPlayerStuck(Float:pos[3], client)
{
    new Float:mins[3];
    new Float:maxs[3];

    GetClientMins(client, mins);
    GetClientMaxs(client, maxs);
    
    // inflate the sizes just a little bit
    for (new i=0; i<sizeof(mins); i++)
    {
        mins[i] -= BOUNDINGBOX_INFLATION_OFFSET;
        maxs[i] += BOUNDINGBOX_INFLATION_OFFSET;
    }

    TR_TraceHullFilter(pos, pos, mins, maxs, MASK_SOLID, TraceEntityFilterPlayer, client);

    return TR_DidHit();
}  

// filter out players, since we can't get stuck on them
public bool:TraceEntityFilterPlayer(entity, contentsMask)
{
    return entity <= 0 || entity > MaxClients;
}

public Action:CreatePropRegister(args)
{
	new String:userid[128];
	new String:propname[1024];
	new String:prophealth[128];
	GetCmdArg(1, userid, sizeof(userid));
	GetCmdArg(2, propname, sizeof(propname));
	GetCmdArg(3, prophealth, sizeof(prophealth));
	PrecacheModel(propname);
	new useridi = StringToInt(userid);
	new useridc = GetClientOfUserId(useridi);
	decl Float:g_fOrigin[3], Float:g_fAngles[3];
	GetClientEyePosition(useridc, g_fOrigin);
	GetClientEyeAngles(useridc, g_fAngles);
            
	TR_TraceRayFilter(g_fOrigin, g_fAngles, MASK_SOLID, RayType_Infinite, Trace_FilterPlayers, useridc);
	if(TR_DidHit(INVALID_HANDLE))
	{
		TR_GetEndPosition(g_fOrigin, INVALID_HANDLE);
		TR_GetPlaneNormal(INVALID_HANDLE, g_fAngles);
		GetVectorAngles(g_fAngles, g_fAngles);
		g_fAngles[0] += 90.0;
                
		new g_iEnt = CreateEntityByName("prop_dynamic");
		ServerCommand("es_xset wcs_lastgive %i", g_iEnt);
		SetEntityModel(g_iEnt, propname);
		DispatchKeyValue(g_iEnt, "targetname", "Name");
		DispatchKeyValue(g_iEnt, "Solid", "6");
		DispatchSpawn(g_iEnt);
		TeleportEntity(g_iEnt, g_fOrigin, g_fAngles, NULL_VECTOR);
		SetEntityMoveType(g_iEnt, MOVETYPE_VPHYSICS);
		if (StringToInt(prophealth) > 0)
		{
			Entity_SetHealth(g_iEnt, StringToInt(prophealth), true, true);
		}
	} 
	
	return Plugin_Handled;
}

public OnEntityCreated(entity, const String:classname[])
{
	if (entity > 0)
	{
		SDKHook(entity, SDKHook_OnTakeDamage, OnTakeDamage);
	}
}

public Action:OnTakeDamage(victim, &attacker, &inflictor, &Float:damage, &damagetype)
{ 
	new health = Entity_GetHealth(victim);
	if (health > 0 && victim > MaxClients)
	{
		Entity_TakeHealth(victim, RoundFloat(damage), true, true);
	}
}

public bool:Trace_FilterPlayers(entity, contentsMask, any:data)
{
    if(entity != data && entity > MaxClients)
        return true;

    return false;
}
