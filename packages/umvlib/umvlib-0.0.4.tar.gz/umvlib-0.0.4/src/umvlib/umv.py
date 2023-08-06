
import xml.etree.ElementTree as ET
import requests
import datetime
import re

class Constants:
    STATUS_APPROVED = 3
    STATUS_REPPROVED = 4

class Fields:
    ID = 'id'
    ACTIVE = 'active'
    ORIGIN = 'origin'
    ALT_ID = 'alternativeIdentifier'
    SITUATION = 'situation'
    FIELD_HISTORY = 'fieldHistory'
    VALUE = 'value'
    VALUE_FOR_EXHIBITION = 'valueForExhibition'
    DESCRIPTION = 'description'
    SCHEDULE = 'schedule'
    SCHEDULE_ITEMS = 'scheduleItems'
    SCHEDULE_ITEM = 'scheduleItem'
    SCHEDULE_TYPE = 'scheduleType'
    SCHEDULE_END_DATE = 'executionEndDate'
    SCHEDULE_END_TIME = 'executionEndTime'
    ACTIVITY = 'activity'
    ACTIVITY_HISTORY = 'activityHistory'
    SERVICE_LOCALS = 'serviceLocals'
    SERVICE_LOCAL = 'serviceLocal'
    SERVICE_LOCAL_ORIGIN = 'serviceLocalOrigin'
    SERVICE_LOCAL_TYPE = 'serviceLocalType'
    CORPORATE_NAME = 'corporateName'
    STREET = 'street'
    STREET_NUMBER = 'streetNumber'
    STREET_COMPLEMENT = 'streetComplement'
    CELLPHONE_NUMBER = 'cellphoneNumber'
    CELLPHONE_DDI = 'cellphoneIdd'
    CELLPHONE_DDD = 'cellphoneStd'
    PHONE_DDI = 'phoneIdd'
    PHONE_DDD = 'phoneStd'
    PHONE_NUMBER = 'phoneNumber'
    NEIGHBORHOOD = 'cityNeighborhood'
    CITY = 'city'
    COUNTRY = 'country'
    STATE = 'state'
    ZIP_CODE = 'zipCode'
    STREET_TYPE = 'streetType'
    EMAIL = 'email'
    AGENT = 'agent'
    AGENTS = 'agents'
    AGENT_INSERT = 'agentInsert'
    AGENT_LAST_UPDATE = 'agentLastUpdate'
    SECTIONS = 'sections'
    SECTION = 'section'
    ITEMS = 'items'
    ITEM = 'item'
    FIELDS = 'fields'
    FIELD = 'field'
    DATE = 'date'
    HOUR = 'hour'
    ATCIVITIES_ORIGIN = 'activitiesOrigin'
    TEAM = 'team'
    TEAM_EXECUTION = 'teamExecution'
    SERVICE_LOCAL = 'serviceLocal'
    ACTIVITY_RELATIONSHIP = 'activityRelationship'
    CUSTOM_FIELDS = 'customFields'
    CUSTOM_FIELD = 'customField'
    CUSTOM_FIELD_VALUES = 'customFieldValues'
    OBSERVATION = 'observation'
    FIELD_TYPE = 'fieldType'
    SCHEDULE_NOTIFICATION = 'scheduleNotification'
    MESSAGE = 'message'
    CALLBACK = 'callback'
    SUB_GROUP = 'subGroup'
    CUSTOM_ENTITY_ENTRY = 'customEntityEntry'
    INITIAL_START_TIME_ON_SYSTEM = 'initialStartTimeOnSystem'
    END_START_TIME_ON_SYSTEM = 'endFinishTimeOnSystem'
    STATUS = 'status'
    STATUS_APPROVAL = 'statusApproval'

f = Fields
c = Constants

class Umov:

    def __init__(self, api_key):        
        self.api_key = api_key        
        self.base_url = f'http://api.umov.me/CenterWeb/api/{self.api_key}'

    def create_custom_entity(self,                             
                             entity: str = None,
                             description: str = None,
                             alternative_identifier: str = None,
                             **kwargs):
        custom_entity = ET.Element(f.CUSTOM_ENTITY_ENTRY)
        
        self._sub_element(custom_entity, f.DESCRIPTION, description)
        self._sub_element(custom_entity, f.ALT_ID, alternative_identifier)

        url = f'{self.base_url}/customEntity/alternativeIdentifier/{entity}/customEntityEntry.xml'
        response = requests.post(url, data={'data': ET.tostring(custom_entity)})
        if response.status_code == 201 or response.status_code == 200:
            print('Response', response.text)
            return alternative_identifier
        else:
            if 'already exists' in response.text or 'alternativeIdentifier' in response.text:
                print(f"Got custom entity {alternative_identifier}")
                return alternative_identifier
            else:
                raise Exception(response.status_code, response.text)

    def create_service_local_type(self,
                                  description: str,
                                  id: int = None,
                                  alternative_identifier: str = None,
                                  active: bool = True):
        s_local_type = ET.Element(f.SERVICE_LOCAL_TYPE)

        self._sub_element(s_local_type, f.DESCRIPTION, description)
        self._sub_element(s_local_type, f.ID, id)
        self._sub_element(s_local_type, f.ALT_ID, alternative_identifier)
        self._sub_element(s_local_type, f.ACTIVE, active)

        url = f'{self.base_url}/serviceLocalType.xml'
        response = requests.post(url, data={'data': ET.tostring(s_local_type)})
        if response.status_code == 201 or response.status_code == 200:
            print('Response', response.text)
            return alternative_identifier
        else:
            if 'alternativeIdentifierAlreadyInUse' in response.text:
                print(f"Got service local {alternative_identifier}")
                return alternative_identifier
            else:
                raise Exception(response.status_code, response.text)

    def _sub_element(self, element: ET.SubElement, key: str, value):
        if value:
            element = ET.SubElement(element, key)
            element.text = str(value).strip()
            return element
        return None

    def create_service_local(self,
                             description: str, active: bool = True, corporate_name: str = None,
                             alternative_identifier: str = None, state: str = None, city: str = None,
                             country: str = None, id: str = None, street: str = None, zip_code: str = None,
                             street_type: str = None, street_number: int = None, street_complement: str = None,
                             cellphone_idd: int = None, cellphone_std: int = None, cellphone_number: int = None,
                             phone_idd: int = None, phone_std: int = None, phone_number: int = None, email: str = None,
                             city_neighborhood: str = None, observation: str = None, service_local_type: str = None):

        service_locals = ET.Element(f.SERVICE_LOCALS)
        s_local = ET.SubElement(service_locals, f.SERVICE_LOCAL)

        self._sub_element(s_local, f.ID, id)
        self._sub_element(s_local, f.ACTIVE, active)
        self._sub_element(s_local, f.ALT_ID, alternative_identifier)
        self._sub_element(s_local, f.DESCRIPTION, description)
        self._sub_element(s_local, f.CORPORATE_NAME, corporate_name)
        self._sub_element(s_local, f.EMAIL, email)
        self._sub_element(s_local, f.OBSERVATION, observation)

        self._sub_element(s_local, f.ZIP_CODE, zip_code)
        self._sub_element(s_local, f.STREET, street)
        self._sub_element(s_local, f.STREET_TYPE, street_type)
        self._sub_element(s_local, f.STREET_NUMBER, street_number)
        self._sub_element(s_local, f.STREET_COMPLEMENT, street_complement)
        self._sub_element(s_local, f.CITY, city)
        self._sub_element(s_local, f.STATE, state)
        self._sub_element(s_local, f.COUNTRY, country)
        self._sub_element(s_local, f.NEIGHBORHOOD, city_neighborhood)

        self._sub_element(s_local, f.CELLPHONE_NUMBER, cellphone_number)
        self._sub_element(s_local, f.CELLPHONE_DDI, cellphone_idd)
        self._sub_element(s_local, f.CELLPHONE_DDD, cellphone_std)
        self._sub_element(s_local, f.PHONE_DDI, phone_idd)
        self._sub_element(s_local, f.PHONE_DDD, phone_std)
        self._sub_element(s_local, f.PHONE_NUMBER, phone_number)

        if service_local_type:
            s_local_type = ET.SubElement(s_local, f.SERVICE_LOCAL_TYPE)
            self._sub_element(s_local_type, f.ALT_ID, service_local_type)

        url = f'{self.base_url}/batch/serviceLocals.xml'
        response = requests.post(
            url,
            data={'data': ET.tostring(service_locals)}
        )
        if response.status_code == 201 or response.status_code == 200:
            print('Response', response.text)
            return alternative_identifier
        else:
            print('data', ET.tostring(service_locals))
            raise Exception(url, response.status_code, response.text)

    def create_schedule(self,
                        service_local: str,
                        date: str = None,
                        hour: str = None,
                        active: bool = True,
                        activities_origin: int = 7,
                        agent: int = None,
                        team: int = None,
                        team_execution: int = None,
                        alternative_identifier: str = None,
                        id: int = None,
                        observation: str = None,
                        origin: int = None,
                        situation: int = 30,
                        schedule_type: str = None,
                        activity_type: str = None,
                        sender_local_id: str = None,
                        **kwargs):

        today = datetime.datetime.now()
        if not date:
            date = today.strftime('%Y-%m-%d')
        if not hour:
            hour = today.strftime('%H:%M')

        schedule = ET.Element(f.SCHEDULE)

        self._sub_element(schedule, f.DATE, date)
        self._sub_element(schedule, f.HOUR, hour)
        self._sub_element(schedule, f.ACTIVE, active)
        self._sub_element(schedule, f.ATCIVITIES_ORIGIN, activities_origin)
        self._sub_element(schedule, f.TEAM, team)
        self._sub_element(schedule, f.TEAM_EXECUTION, team_execution)
        self._sub_element(schedule, f.ALT_ID, alternative_identifier)
        self._sub_element(schedule, f.ID, id)
        self._sub_element(schedule, f.OBSERVATION, observation)
        self._sub_element(schedule, f.ORIGIN, origin)

        _custom_fields = ET.SubElement(schedule, f.CUSTOM_FIELDS)
        for key, value in kwargs.items():            
            _cf = ET.SubElement(_custom_fields, key)  
            self._sub_element(_cf, f.ALT_ID, value)            

        _agent = ET.SubElement(schedule, f.AGENT)
        self._sub_element(_agent, f.ALT_ID, agent)

        _service_local = ET.SubElement(schedule, f.SERVICE_LOCAL)
        self._sub_element(_service_local, f.ALT_ID, service_local)

        _schedule_type = ET.SubElement(schedule, f.SCHEDULE_TYPE)
        self._sub_element(_schedule_type, f.ALT_ID, schedule_type)

        _situation = ET.SubElement(schedule, f.SITUATION)
        self._sub_element(_situation, f.ID, situation)

        if activity_type:
            activity_relationship = ET.SubElement(
                schedule, f.ACTIVITY_RELATIONSHIP)
            activity = ET.SubElement(activity_relationship, f.ACTIVITY)
            self._sub_element(activity, f.ALT_ID, activity_type)

        if sender_local_id:
            s_local_origin = ET.SubElement(schedule, f.SERVICE_LOCAL_ORIGIN)
            self._sub_element(s_local_origin, f.ALT_ID, sender_local_id)

        print('sched_data', ET.tostring(schedule))
        url = f'{self.base_url}/schedule.xml'
        response = requests.post(url, data={'data': ET.tostring(schedule)})
        if (response.status_code == 201):
            print('Response', response.text)
            return alternative_identifier
        else:            
            raise Exception(url, response.status_code, response.text)

    def create_items(self, items):
        print(items)
        URL = f'{self.base_url}/batch/items.xml'

        items_to_create = ET.Element(f.ITEMS)

        max_list_size = 50  # API limit
        list_of_items_list = list()

        for i in range(0, len(items), max_list_size):
            list_of_items_list.append(items[i:i+max_list_size])

        for items_list in list_of_items_list:
            for item in items_list:
                alt_id = str(item["alt_id"])
                description = str(
                    re.sub(r'[^a-zA-Z0-9 ()-]', '', item["description"].upper()))

                new_item = ET.SubElement(items_to_create, f.ITEM)
                ET.SubElement(new_item, f.ALT_ID).text = alt_id
                ET.SubElement(new_item, f.DESCRIPTION).text = description
                sub_group = ET.SubElement(new_item, f.SUB_GROUP)
                ET.SubElement(sub_group, f.ALT_ID).text = "01"
            response = requests.post(
                URL, data={'data':  ET.tostring(items_to_create)})
            if response.status_code >= 400:
                raise Exception(URL, response.status_code, response.text)

    def add_schedule_items(self, schedule_id, items):
        URL = f'{self.base_url}/batch/scheduleItems.xml'

        schedule_items = ET.Element(f.SCHEDULE_ITEMS)
        for item in items:

            alt_id = str(item["alt_id"])
            quantity = str(float(item["quantity"]))

            schedule_item = ET.SubElement(schedule_items, f.SCHEDULE_ITEM)
            schedule = ET.SubElement(schedule_item, f.SCHEDULE)
            ET.SubElement(schedule, f.ALT_ID).text = schedule_id
            item = ET.SubElement(schedule_item, f.ITEM)
            ET.SubElement(item, f.ALT_ID).text = alt_id
            custom_fields = ET.SubElement(schedule_item, f.CUSTOM_FIELDS)
            ET.SubElement(custom_fields, 'quantidade').text = quantity

        response = requests.post(
            URL, data={'data':  ET.tostring(schedule_items)})
        if response.status_code == 200:
            print('Response', response.text)
        else:
            raise Exception(URL, response.status_code, response.text)

    def approve_activity_history(self, execution_id):
        URL = f'{self.base_url}/activityHistory/{execution_id}.xml'

        activity_history = ET.Element(f.ACTIVITY_HISTORY)
        self._sub_element(activity_history, f.STATUS_APPROVAL, c.STATUS_APPROVED)
        response = requests.post(URL, data={'data': ET.tostring(activity_history)})
        if response.status_code == 200:
            print('Response', response.text)
        else:
            raise Exception(URL, response.status_code, response.text)