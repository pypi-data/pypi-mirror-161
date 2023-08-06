from requests import Session
import pymssql
from .resource import *


class Ddsf():
    """
    object that stores session

    Parameters
    ----------
    url
        dsf url
    auth
        auth object: HTTPBasicAuth or HttpNtlmAuth
    """
    url = None
    session = None
    db = None

    def __init__(self, url, auth):
        self.url = url
        self.session = Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.session.auth = auth

    def connectdb(self, host, database, user, password):
        """
        initialize database connection for the use of non-dsf functions
        """
        self.db = pymssql.connect(host, user, password, database, autocommit=True)

    def getSingle(self, entity, obj, filter=""):
        if filter:
            filter = "?$filter=" + filter
        response = self.session.get(self.url + entity + filter)
        if 'value' not in response.json() or not response.json()['value']:
            return None
        return obj(self.url, self.session, response.json()['value'][0], self.db)

    def getMultiple(self, entity, obj, filter=""):
        if filter:
            filter = "?$filter=" + filter
        orgUnits = []

        response = self.session.get(self.url + entity + filter)
        if 'value' not in response.json() or not response.json()['value']:
            return []

        # this loop runs minimum the first time(indicated by empty orgUnits) and repeats if the response contains a nextLink
        while not orgUnits or '@odata.nextLink' in response.json():
            if orgUnits:
                response = self.session.get(response.json()['@odata.nextLink'])

            for orgUnit in response.json()['value']:
                orgUnits.append(obj(self.url, self.session, orgUnit))

        return orgUnits

    def now(self):
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S+01:00")

    def addProlongation(self, studyid, reason, approvedBy, time):
        data = {"Studies": studyid,
                "ApprovedOn": time,
                "ApprovedBy": approvedBy,
                "NumberOfPeriods": 1,
                "Reason": reason,
                "ApprovedProlongingPeriods": 99}
        newProlongation = StudiesProlongation(self.url, self.session, data, db=self.db)
        return newProlongation.post()

    def actorToActorTypes(self, filter=None):
        """
        get Mappings between an Actor and an ActorType

        Args:
            filter: dsf filter

        Returns:
            list[ActorToActorType]: list of ActorToActorTypes

        """
        return self.getMultiple("ActorToActorType()", ActorToActorType, filter)

    def actorTypes(self):
        """
        get list of all ActorTypes

        Returns:
            list[ActorType]: list of ActorTypes

        """
        return self.getMultiple("ActorType()", ActorType)

    def study(self, studyid):
        """
        find a study by studyid

        Args:
            studyid: studyid

        Returns:
            Studies: a Studies object

        """
        return self.getSingle("Studies()",
                              Studies,
                              f"StudiesId eq {studyid}")

    def user(self, username):
        """
        find a user by username

        Args:
            username: zih-login

        Returns:
            UserAccount: a user object

        """
        return self.getSingle("UserAccount()",
                              UserAccount,
                              f"UserName eq '{username}'")

    def userGroups(self):
        """
        get all usergroups

        """
        return self.getMultiple("UserGroup()",
                                UserGroup)

    def userGroup(self, name):
        """
        find a usergroup by name

        Args:
            name: name of the group

        Returns:
            UserGroup: a usergroup object

        """
        return self.getSingle("UserGroup()",
                              UserGroup,
                              f"UserGroupName eq '{name}'")

    def studentByPersonId(self, personId):
        """
        find a student by personId

        Args:
            personId(int): personId

        Returns:
            Student: a student object

        """
        return self.getSingle("Student()",
                              Student,
                              f"PersonId eq {personId}")

    def student(self, matric):
        """
        find a student by matriculation number

        Args:
            matric(int): matriculationNumber

        Returns:
            Student: a student object

        """
        return self.getSingle("Student()",
                              Student,
                              f"MatriculationNumber eq '{matric}'")

    def payments(self, filter=''):
        return self.getMultiple("Payment()", Payment, filter)

    def activities(self, personid):
        return self.getMultiple("Activity()",
                                Activity,
                                f"Actor eq {personid}")

    def studyProcessStudies(self, personid):
        """
        get StudyProcessStudies of a person

        Args:
            personid(int): id of a person

        Returns:
            StudyProcessStudies: a StudyProcessStudies object
        """
        return self.getMultiple("StudyProcessStudies()",
                                StudyProcessStudies,
                                f"Student eq {personid}")

    def room(self, id, full=False):
        """
        get a specific room

        Args:
            id: RoomId to search for
            full: if True it will replace RoomType with the corresponding object

        Returns:
            Room: Room with the given id

        """
        if not full:
            return self.getSingle("Room()",
                                  Room,
                                  f"RoomId eq {id}")
        room = self.getSingle("Room()",
                              Room,
                              f"RoomId eq {id}")
        room.RoomType = room.type()
        return room

    def rooms(self):
        """
        get all available rooms

        Returns:
            list[Room]: a list of Room

        """
        return self.getMultiple("Room()", Room, "IsDeleted eq false")

    def orgUnits(self, filter="IsDeleted eq false"):
        """
        get all available orgUnits

        Returns:
            list[OrgUnit]: a list of OrgUnits

        """
        return self.getMultiple("OrgUnit()", OrgUnit, filter)

    def orgUnitType(self, filter=""):
        """
        get all available orgUnitTypes

        Returns:
            list[OrgUnitType]: a list of OrgUnitType

        """
        return self.getSingle("OrgUnitType()", OrgUnitType, filter)

    def orgUnitTypes(self):
        """
        get all available orgUnitTypes

        Returns:
            list[OrgUnitType]: a list of OrgUnitType

        """
        return self.getMultiple("OrgUnitType()", OrgUnitType)

    def roomTypes(self):
        """
        get all available roomTypes

        Returns:
            list[RoomType]: a list of RoomType

        """
        return self.getMultiple("RoomType()", RoomType, "IsDeleted eq false")

    def mailingListId(self, name):
        """
        get MailingListId of a given MailingListName

        Args:
            name(str): name of the MailingList

        Returns:
            MailingListId(int): id of the MailingList
        """
        result = self.session.get(f"{self.url}MailingList()?$filter=MailingListName eq '{name}'").json()['value']
        if not result:
            return None
        return result[0]['MailingListId']

    def mailingListActor(self, id):
        """
        get all Members of a MailingList

        Args:
            id(int): id of the mailingList

        Returns:
            list[MailingListActor]: all Members
        """
        return self.getMultiple("MailingListActor", MailingListActor, f"MailingList eq {id}")

    def person(self, id):
        return self.getSingle("Person()", Person, f"ActorId eq {id}")

    def persons(self, filter=""):
        return self.getMultiple("Person()", Person, filter)

    def academicTitles(self):
        return self.getMultiple("AcademicTitle()", RoomType, "IsDeleted eq false")

    def academicTitle(self, id=None):
        title = AcademicTitle(self.url, self.session)
        title.get(id)
        return title

    def get(self, url=None):
        if not url:
            url = self.url
        return self.session.get(url).json()['value']
