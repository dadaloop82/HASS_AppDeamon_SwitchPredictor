#  _    _                                               _              _
# | |  | |                          /\           (_)   | |            | |
# | |__| | ___  _ __ ___   ___     /  \   ___ ___ _ ___| |_ __ _ _ __ | |_
# |  __  |/ _ \| '_ ` _ \ / _ \   / /\ \ / __/ __| / __| __/ _` | '_ \| __|
# | |  | | (_) | | | | | |  __/  / ____ \\__ \__ \ \__ \ || (_| | | | | |_
# |_|  |_|\___/|_| |_| |_|\___| /_/    \_\___/___/_|___/\__\__,_|_| |_|\__|
#    ___                                  _ _   _
#   / _ \_____      _____ _ __  __      _(_) |_| |__
#  / /_)/ _ \ \ /\ / / _ \ '__| \ \ /\ / / | __| '_ \
# / ___/ (_) \ V  V /  __/ |     \ V  V /| | |_| | | |
# \/    \___/ \_/\_/ \___|_|      \_/\_/ |_|\__|_| |_|
# /\_/\___  _   _ _ __    / __\___  _ __ | |_ _ __ ___ | | / \
# \_ _/ _ \| | | | '__|  / /  / _ \| '_ \| __| '__/ _ \| |/  /
#  / \ (_) | |_| | |    / /__| (_) | | | | |_| | | (_) | /\_/
#  \_/\___/ \__,_|_|    \____/\___/|_| |_|\__|_|  \___/|_\/
#
# Github:
# https://github.com/dadaloop82/HASS_AppDeamon_SwitchPredictor
#
# I have a dream:
# - make my life smarter without creating any automation!
#
# Ingredients:
# - Working instance of Home Assistant (https://www.home-assistant.io/)
# - Working addon appDeamon for HASS (https://github.com/AppDaemon/appdaemon)
# - Optional influxDB database - otherwise takes data from history (they are limited!)
#
# Operating idea:
# - Based on the analysis of the change of a certain switch
# - (set in configuration), the system analyzes the change of the sensors in that moment
# - So it creates a model, divided by periods (including seasons, etc. ..)
# - trying to guess their habits and if the conditions are similar, it proposes via Alexa
# - the activation of the switch, learning from the answers given.
# - If the probability of activation is very high,
# - the action could be performed automatically without any iteration with the user.
#
#
# influxdb_client are installed with requirements.txt [...]/appdeamon/config/apps/
# from influxdb_client import InfluxDBClient

# python module imports
import hassapi as hass


class Constant:
    def __init__(self):
        self.DateTime_TZ = "%Y-%m-%dT%H:%M:%S+00:00"
        self.DateTime_msTZ = "%Y-%m-%dT%H:%M:%S.%f+00:00"
        self.Time_short = "%H:%M"
        self.Path_Model = "models"
        self.UseInfluxDB = False


class Config:
    def __init__(self, hass, constant):
        self._hass = hass
        self.constant = constant
        self.configParms = self._hass.args["config"]
        self.currentConfig = {}
        self.useInfluxDB = False

        # default value of parameters
        self.defaultParams = {
            "historyday": 30,
            "timerangehistoryseconds": 0,
            "mergeonperiodminutes": 15,
            "roundtimeevents": 15,
            "excludetimeslotpercentage": 30,
            "timezone": "Europe/Rome",
            "useinfluxdb": False
        }

        # read the config
        self.readConfig()

        if self.currentConfig["useinfluxdb"]:
            # setup the influxDB boolean
            self.constant.UseInfluxDB = True

    def readConfig(self):
        for key, value in self.defaultParams.items():
            if key in self.configParms:
                self.currentConfig[key] = self.configParms[key]
            else:
                self.currentConfig[key] = value

    def getConfig(self, key):
        if not key:
            return self.currentConfig


class historyDB:
    def __init__(self, hass, constant):
        self._hass = hass
        self.constant = constant

        # import influxDB library if influxDB are enable
        if constant.UseInfluxDB:
            try:
                influxbModule = __import__("influxdb_client")
                self.InfluxDBClient = influxbModule.InfluxDBClient
            except:
                self._hass.log(
                    "InfluxDB enabled but library are not loaded in AppDeamon, fallback to HASS history (limited!)", level="WARNING")
                self.constant.UseInfluxDB = False


class Utility:
    def __init__(self, hass, constant):
        self._hass = hass
        self.constant = constant


class HassPredictSwitch(hass.Hass):

    # initialize Class
    def initialize(self):

        # log
        self.log("Starting new instance", level="INFO")

        # init the classes
        _constant = Constant()
        _config = Config(self, _constant)
        _utility = Utility(self, _constant)
        _historydb = historyDB(self, _constant)


# import datetime
# import time
# import os
# import json
# import hashlib

# from os.path import exists


# class HassPredictSwitch(hass.Hass):

#     # initialize Class
#     def initialize(self):
        # self.log("Starting new instance", level="INFO")

        # # init object of current Model
        # currentModel = _utility.CurrentModel()

        # print(currentModel.getCurrentModel())

        # # get the configuration
        # configData = _config.CurrentConfig()

        # print(configData.getCurrentConfig())

        # baseswitch_historys = []
        # averageObject = {}
        # OnStatePeriod = {'start': None, 'end': None}
        # isDataLoadedFromFile = False
        # dayHistoryPeriod = configGet('historyday')
        # firstDateWithNoHistory = self._currentDateTime

        # for event in configGet('predictsevent'):

        #     currentDateTime = self._currentDateTime

        #     # get baseswitch
        #     baseswitch = configGet(['predictsevent', event, 'basewitch'])

        #     # set configHash
        #     configHash = [baseswitch, configGet(
        #         ['predictsevent', event, 'basedon'])]
        #     configHashMd5 = hashlib.md5(
        #         ''.join(map(str, configHash)).encode('utf-8')).hexdigest()

        #     # check if model is already saved
        #     fileName = os.path.join(_currentfolder, MODELPATH, f"{event}.json")

        #     if exists(fileName):

        #         # if the file exist, read the json data (model)
        #         log.info(f"{event}: model already exist - load and use them ")
        #         fileEventCached = open(fileName,)

        #         # put the data on entityStates variable
        #         entityStatesTmp = json.load(fileEventCached)

        #         if entityStatesTmp and 'confighash' in entityStatesTmp and entityStatesTmp['confighash'] == configHashMd5:
        #             # set the savedModelEventsHistoryStartDate|EndDate and the flag in isDataLoadedFromFile
        #             entityStates = entityStatesTmp
        #             savedModelEventsHistoryEndDate = datetime.strptime(
        #                 entityStates['updatedate'][0], DATETIME_FORMAT)
        #             savedModelEventsHistoryStartDate = datetime.strptime(
        #                 entityStates['updatedate'][1], DATETIME_FORMAT)
        #             isDataLoadedFromFile = True
        #         else:
        #             log.warning(
        #                 f"{event}: model file are not valid or config are changed")

        #         fileEventCached.close()

        #     # get history of baseswitch
        #     log.debug(f"ask baseSwitch: {baseswitch} history ")

        #     # calculate che number of cycles
        #     cycle = int(dayHistoryPeriod/10)+1

        #     # start cycle
        #     for number in range(0, cycle):

        #         # calculate start and end period
        #         startDayPeriod = number*10
        #         endDayPeriod = startDayPeriod+10

        #         # if exceed, get the value in config
        #         if endDayPeriod > dayHistoryPeriod:
        #             endDayPeriod = dayHistoryPeriod

        #         # calculate date
        #         endDate = getdifferncedate(
        #             currentDateTime.replace(hour=23, minute=59, second=00, microsecond=00), "days", startDayPeriod)
        #         startDate = getdifferncedate(
        #             currentDateTime.replace(hour=23, minute=59, second=00, microsecond=00), "days", endDayPeriod)

        #         if endDate > currentDateTime:
        #             endDate = currentDateTime.replace(
        #                 second=00, microsecond=00)

        #         log.info(
        #             f"{event}: date requested: {startDate} - {endDate}")

        #         if isDataLoadedFromFile:
        #             log.info(
        #                 f"{event}: date in cached:  {savedModelEventsHistoryStartDate} - {savedModelEventsHistoryEndDate}")

        #         # if is file loaded, check if the startDate are NOT between the already laoaded data
        #         if(isDataLoadedFromFile and startDate >= savedModelEventsHistoryStartDate):
        #             startDate = savedModelEventsHistoryEndDate

        #         # check if startDate is greater than enDate -> the data must be loaded from file
        #         if isDataLoadedFromFile and startDate >= savedModelEventsHistoryStartDate and endDate <= savedModelEventsHistoryEndDate:
        #             log.info(
        #                 f"{event}: get data from cache: {startDate}/{endDate}")

        #         else:
        #             # get history for this timeslot
        #             log.info(
        #                 f"{event}: ask history {startDate} - {endDate} )")

        #             history = self.get_history(
        #                 entity_id=baseswitch, start_time=startDate, end_time=endDate)

        #             # no history for this time period
        #             if not history:
        #                 log.warning(
        #                     f"{event}: no history provided from {startDayPeriod} days ago")
        #                 if not firstDateWithNoHistory:
        #                     firstDateWithNoHistory = endDate
        #                 break

        #             # if this is a single day, the history is not array
        #             if len(history) > 0:
        #                 history = history[0]

        #             # append all to historys
        #             baseswitch_historys = baseswitch_historys + history

        #     # cycle baseswitch history events
        #     if not isDataLoadedFromFile:
        #         log.info(
        #             f"{event}: history data to analyze NEW: {len(baseswitch_historys)}")
        #     elif len(baseswitch_historys):
        #         log.info(
        #             f"{event}: history data to analyze UPDATE: {len(baseswitch_historys)}")

        #     # set updatetime
        #     entityStates['updatedate'] = [
        #         self._currentDateTime.strftime(DATETIME_FORMAT),
        #         (endDate if firstDateWithNoHistory else firstDateWithNoHistory).replace(
        #             hour=00, minute=00, second=00, microsecond=00).strftime(DATETIME_FORMAT)
        #     ]

        #     # set configHash
        #     configHash = [baseswitch, configGet(
        #         ['predictsevent', event, 'basedon'])]
        #     entityStates['confighash'] = configHashMd5

        #     startAnalyzingTime = time.time()
        #     countMergedOnTimeSlot = 0
        #     isThisOnPeriod = False
        #     ###############################################################
        #     # BASE SWITCH ROUTINE
        #     # - TIME SLOT CALCULATION
        #     #   array structure
        #     #   [0] = count
        #     #   [1] = startTime
        #     #   [2] = endTime
        #     #   [3] = weekday (0-6)
        #     #   [4] = season (0-3)
        #     ###############################################################

        #     for baseSwitchHistory in baseswitch_historys:

        #         # get and convert the hystory Date
        #         historyDateTime = convertdatatime(
        #             baseSwitchHistory['last_changed'])

        #         # set a variable with the date rounded by config value
        #         historyTimeRounded = roundDateByMinutes(
        #             historyDateTime, datetime.timedelta(minutes=configGet('roundtimeevents')))

        #         # set a variable with this state of baseSwitch
        #         baseSwitchHistoryState = baseSwitchHistory['state']

        #         # if the state are ON and we are not already onStatePeriod (on-off)
        #         if baseSwitchHistoryState == "on" and not isThisOnPeriod:
        #             # PERIOD ON START
        #             isThisOnPeriod = True
        #             OnStatePeriod['start'] = historyTimeRounded

        #         elif baseSwitchHistoryState == "off" and isThisOnPeriod:
        #             # PERIOD ON END
        #             isThisOnPeriod = False
        #             OnStatePeriod['end'] = historyTimeRounded

        #             # check for period's merge
        #             k = 0
        #             merged = False
        #             for periodOn in entityStates['bt']['timeslot']:

        #                 if periodOn[3] == historyDateTime.weekday() and periodOn[4] == getSeasonByDate(historyDateTime):

        #                     timePeriod = [datetime.strptime(
        #                         periodOn[1], "%H:%M"), datetime.strptime(periodOn[2], "%H:%M")]

        #                     diffStart = int(
        #                         (timePeriod[0] - OnStatePeriod['start']).total_seconds()/60)
        #                     diffEnd = int(
        #                         (timePeriod[1] - OnStatePeriod['end']).total_seconds()/60)

        #                     if diffStart > 0 and abs(diffStart) <= configGet('mergeonperiodminutes'):

        #                         entityStates['bt']['timeslot'][k][1] = OnStatePeriod['start'].strftime(
        #                             ONPERIOD_DATETIME_FORMAT)

        #                         # increase counter
        #                         entityStates['bt']['timeslot'][k][0] += 1
        #                         if entityStates['bt']['timeslot'][k][0] > entityStates['bt']['TSmaxcount']:
        #                             entityStates['bt']['TSmaxcount'] = entityStates['bt']['timeslot'][k][0]

        #                         merged = True

        #                     if diffEnd < 0 and abs(diffEnd) <= configGet('mergeonperiodminutes'):
        #                         entityStates['bt']['timeslot'][k][2] = OnStatePeriod['end'].strftime(
        #                             ONPERIOD_DATETIME_FORMAT)

        #                         merged = True

        #                 k += 1

        #             # save period on array
        #             if merged == False:
        #                 entityStates['bt']['timeslot'].append(
        #                     [
        #                         # count
        #                         1,
        #                         # start time
        #                         OnStatePeriod['start'].strftime(
        #                             ONPERIOD_DATETIME_FORMAT),
        #                         # end time
        #                         OnStatePeriod['end'].strftime(
        #                             ONPERIOD_DATETIME_FORMAT),
        #                         # weekday (0-6)
        #                         historyDateTime.weekday(),
        #                         # season
        #                         getSeasonByDate(historyDateTime)
        #                     ]
        #                 )
        #             else:
        #                 countMergedOnTimeSlot += 1

        #         ###############################################################
        #         # BASED ON ENTITIES ROUTINE
        #         ###############################################################
        #         # cycle of all basedOn Entities

        #         for basedonEntity in configGet(['predictsevent', event, 'basedon']):

        #             # calculate period from time by config to switchBase changed event
        #             startHistory = historyDateTime - \
        #                 datetime.timedelta(seconds=configGet(
        #                     'timerangehistoryseconds'))
        #             endHistory = historyDateTime + \
        #                 datetime.timedelta(seconds=configGet(
        #                     'timerangehistoryseconds'))

        #             # logging
        #             log.debug(
        #                 f"history: {basedonEntity} from {startHistory} for {configGet('timerangehistoryseconds')} sec")

        #             # ask history
        #             basedOnEntityHistorys = self.get_history(
        #                 entity_id=basedonEntity, end_time=endHistory, start_time=startHistory)

        #             # check if exist
        #             if basedOnEntityHistorys:

        #                 # logging
        #                 log.debug(
        #                     f"get {len(basedOnEntityHistorys[0])} history items")

        #                 # init object if is'nt inited
        #                 entityStates['bo'] = setifnotexist(
        #                     entityStates['bo'], basedonEntity, {'type': None})

        #                 # cycle of basedOn entity history
        #                 for basedOnEntityHistory in basedOnEntityHistorys[0]:

        #                     # get state
        #                     state = basedOnEntityHistory['state']

        #                     if state in ['on', 'off'] or isinstance(state, str) and not stringisnumber(state):
        #                         ############################################################
        #                         # BASEDONENTITY STATE ARE BOOLEAN OR STRING
        #                         ############################################################

        #                         # set the type for futhure use
        #                         entityStates['bo'][basedonEntity]['type'] = "string"

        #                         # init the object if is'nt initied
        #                         entityStates['bo'][basedonEntity] = setifnotexist(
        #                             entityStates['bo'][basedonEntity], state, {'count': 0})

        #                         # increment value of this state hits
        #                         entityStates['bo'][basedonEntity][state]['count'] += 1

        #                         # calculate the probability
        #                         # (count of this state * 100)/lenght of history of base switchg
        #                         # entityStates['bo'][basedonEntity][state]['probs'] = round((
        #                         #     entityStates['bo'][basedonEntity][state]['count'] * 100)/len(baseswitch_historys), 2)

        #                     if stringisnumber(state):
        #                         ############################################################
        #                         # BASEDONENTITY STATE ARE INTEGER OR FLOAT
        #                         ###########################################################

        #                         # set the type for futhure use
        #                         entityStates['bo'][basedonEntity]['type'] = "float"

        #                         # get numerico state
        #                         valueState = float(state)

        #                         # set averageObject if aren't setted
        #                         averageObject = setifnotexist(
        #                             averageObject, basedonEntity, [])

        #                         # append the valueState (numeric)
        #                         averageObject[basedonEntity].append(valueState)

        #                         # init the object with min/max/average key if is'nt inited
        #                         entityStates['bo'][basedonEntity] = setifnotexist(
        #                             entityStates['bo'][basedonEntity], 'min', valueState)
        #                         entityStates['bo'][basedonEntity] = setifnotexist(
        #                             entityStates['bo'][basedonEntity], 'max', valueState)
        #                         entityStates['bo'][basedonEntity] = setifnotexist(
        #                             entityStates['bo'][basedonEntity], 'average', valueState)
        #                         entityStates['bo'][basedonEntity] = setifnotexist(
        #                             entityStates['bo'][basedonEntity], 'count', 0)

        #                         # calculate the min, the max and the average
        #                         if valueState < entityStates['bo'][basedonEntity]['min']:
        #                             entityStates['bo'][basedonEntity]['min'] = valueState
        #                         if valueState > entityStates['bo'][basedonEntity]['max']:
        #                             entityStates['bo'][basedonEntity]['max'] = valueState
        #                         entityStates['bo'][basedonEntity]['count'] += 1
        #                         entityStates['bo'][basedonEntity]['average'] = round((
        #                             entityStates['bo'][basedonEntity]['min']+entityStates['bo'][basedonEntity]['max'])/2, 2)
        #     if countMergedOnTimeSlot:
        #         log.info(
        #             f"{event}: merged {countMergedOnTimeSlot} ON timeslot ")

        #     log.info(
        #         f"{event}: model created in {round((time.time())-startAnalyzingTime,2)} sec. - now filtering")

        #     # filter the timeslot by count - calculate on percentage by config
        #     entityStates['bt']['timeslot'] = [
        #         i for i in entityStates['bt']['timeslot'] if i[0] > int((entityStates['bt']['TSmaxcount']/100) *
        #                                                                 configGet("excludetimeslotpercentage"))]
        #     if len(baseswitch_historys):
        #         # convert to json and write on file
        #         fileEventSave = open(os.path.join(_currentfolder,
        #                                           MODELPATH, f"{event}.json"), "w")
        #         fileEventSave.write(json.dumps(entityStates))
        #         fileEventSave.close()

        #         if isDataLoadedFromFile:
        #             log.info(f"{event}: model UPDATED")
        #         else:
        #             log.info(f"{event}: model CREATED  ")
        #     else:
        #         log.info(f"{event}: model not touched")

        #     print(entityStates)
