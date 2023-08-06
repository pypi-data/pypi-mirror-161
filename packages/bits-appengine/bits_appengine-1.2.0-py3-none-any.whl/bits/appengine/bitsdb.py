# -*- coding: utf-8 -*-
"""BITSdb API class file."""

import google.auth
from .endpoints import Endpoints
from bits.google import Google


class BITSdb(Endpoints.Client):
    """BITSdb class."""

    def __init__(
        self,
        api_key=None,
        base_url='http://localhost:8080',
        api='bitsdb',
        version='v1',
        verbose=False,
    ):
        """Initialize a BITSdb class instance."""
        Endpoints.Client.__init__(
            self,
            api_key=api_key,
            base_url=base_url,
            api=api,
            version=version,
            verbose=verbose,
        )
        self.bitsdb = self.service

    def get_datastore_entities(self, kind):
        """Return a list of entities from datastore."""
        _, project = google.auth.default()
        datastore_project = project.replace('-app', '-api')
        print('Datastore Project: {}'.format(datastore_project))
        g = Google()
        data = []
        for entity in g.datastore(datastore_project).list_entities(kind):
            data.append(dict(entity))
        return data
        # return g.datastore(datastore_project).list_entities(kind)

    def get_firestore_docs(self, collection):
        """Return a list of docs from firestore."""
        _, project = google.auth.default()
        firestore_project = project.replace('-app', '')
        print('Firestore Project: {}'.format(firestore_project))
        g = Google()
        data = []
        for doc in g.firestore(firestore_project).get_docs(collection):
            data.append(doc.to_dict())
        return data
        # return g.firestore(firestore_project).get_docs(collection)

    # convert a list to a dict
    def to_json(self, items, key='id'):
        """Return a dict of items."""
        data = {}
        for i in items:
            k = i.get(key)
            data[k] = i
        return data

    # accounts
    def get_account(self, username):
        """Return an Account from BITSdb."""
        return self.bitsdb.accounts().get(id=username).execute()

    def get_accounts(self):
        """Return a list of Accounts from BITSdb."""
        # accounts = self.get_memcache_group('accounts')
        # if accounts is not None:
        #     return accounts
        # params = {'limit': 1000}
        # accounts = self.get_paged_list(self.bitsdb.accounts(), params)
        accounts = self.get_datastore_entities('Account')
        # self.save_memcache_group('accounts', accounts, 'id')
        return accounts

    # ad groups
    def get_ad_group(self, group):
        """Return an AdGroup from BITSdb."""
        return self.bitsdb.ad().groups().get(id=group).execute()

    def get_ad_groups(self):
        """Return a list of AdGroups from BITSdb."""
        # key = 'ad_groups'
        # ad_groups = memcache.get(key)
        # if ad_groups is not None:
        #     return ad_groups
        params = {'limit': 1000}
        ad_groups = self.get_paged_list(self.bitsdb.ad().groups(), params)
        # memcache.add(key, ad_groups, self.memcache_time)
        return ad_groups

    # ad groups syncs
    def add_ad_groups_sync(self, body):
        """Add a new AdGroupSync to BITSdb."""
        return self.bitsdb.ad().groups().syncs().insert(body=body).execute()

    def get_ad_groups_sync(self, sync_id):
        """Return a list of AdGroupSync from BITSdb."""
        return self.bitsdb.ad().groups().syncs().get(id=sync_id).execute()

    def get_ad_groups_syncs(self):
        """Return a list of AdGroupSync from BITSdb."""
        response = self.bitsdb.ad().groups().syncs().list().execute()
        return response.get('items', [])

    # ad users
    def get_ad_user(self, user):
        """Return an AdUser from BITSdb."""
        return self.bitsdb.ad().users().get(id=user).execute()

    def get_ad_users(self):
        """Return a list of AdUsers from BITSdb."""
        # ad_users = self.get_memcache_group('ad_users')
        # if ad_users is not None:
        #     return ad_users
        params = {'limit': 1000}
        ad_users = self.get_paged_list(self.bitsdb.ad().users(), params)
        # self.save_memcache_group('ad_users', ad_users, 'username')
        return ad_users

    # AWS
    def add_aws_account(self, body):
        """Add a new AwsAccount to BITSdb."""
        return self.bitsdb.aws().accounts().insert(body=body).execute()

    def get_aws_account(self, account_id):
        """Return an AwsAccount from BITSdb."""
        return self.bitsdb.aws().accounts().get(id=account_id).execute()

    def get_aws_accounts(self):
        """Return a list of AWS Accounts from BITSdb."""
        # key = 'aws_accounts'
        # aws_accounts = memcache.get(key)
        # if aws_accounts is not None:
        #     return aws_accounts
        params = {'limit': 1000}
        aws_accounts = self.get_paged_list(self.bitsdb.aws().accounts(), params)
        # memcache.add(key, aws_accounts, self.memcache_time)
        return aws_accounts

    # Cost Objects
    def add_costobject(self, body):
        """Add a new AwsAccount to BITSdb."""
        return self.bitsdb.costobjects().insert(body=body).execute()

    def get_costobject(self, costobject):
        """Return an AwsAccount from BITSdb."""
        return self.bitsdb.costobjects().get(id=costobject).execute()

    def get_costobjects(self):
        """Return a list of CostObjects from BITSdb."""
        # costobjects = self.get_memcache_group('costobjects')
        # if costobjects is not None:
        #     return costobjects
        params = {'limit': 1000}
        costobjects = self.get_paged_list(self.bitsdb.costobjects(), params)
        # self.save_memcache_group('costobjects', costobjects, 'costobject')
        return costobjects

    # DNS

    # dns cname records
    def get_dns_cname_records(self):
        """Return a list of CnameRecords from BITSdb."""
        # key = 'dns_cname_records'
        # dns_cname_records = memcache.get(key)
        # if dns_cname_records is not None:
        #     return dns_cname_records
        params = {'limit': 1000}
        dns_cname_records = self.get_paged_list(self.bitsdb.dns().cname_records(), params)
        # memcache.add(key, dns_cname_records, self.memcache_time)
        return dns_cname_records

    # dns mx records
    def get_dns_mx_records(self):
        """Return a list of MxRecords from BITSdb."""
        # key = 'dns_mx_records'
        # dns_mx_records = memcache.get(key)
        # if dns_mx_records is not None:
        #     return dns_mx_records
        params = {'limit': 1000}
        dns_mx_records = self.get_paged_list(self.bitsdb.dns().mx_records(), params)
        # memcache.add(key, dns_mx_records, self.memcache_time)
        return dns_mx_records

    # dns ns records
    def get_dns_ns_records(self):
        """Return a list of NsRecords from BITSdb."""
        # key = 'dns_ns_records'
        # dns_ns_records = memcache.get(key)
        # if dns_ns_records is not None:
        #     return dns_ns_records
        params = {'limit': 1000}
        dns_ns_records = self.get_paged_list(self.bitsdb.dns().ns_records(), params)
        # memcache.add(key, dns_ns_records, self.memcache_time)
        return dns_ns_records

    # filesystems
    def get_filesystems(self):
        """Return a list of Filesystems from BITSdb."""
        # filesystems = self.get_memcache_group('filesystems')
        # if filesystems is not None:
        #     return filesystems
        params = {'limit': 1000}
        filesystems = self.get_paged_list(self.bitsdb.filesystems(), params)
        # self.save_memcache_group('filesystems', filesystems, 'server')
        return filesystems

    # github teams syncs
    def add_github_teams_sync(self, body):
        """Add a new GithubTeamSync to BITSdb."""
        return self.bitsdb.github().teams().syncs().insert(body=body).execute()

    def get_github_teams_sync(self, team_id):
        """Return a GithubTeamSync from BITSdb."""
        return self.bitsdb.github().teams().syncs().get(id=team_id).execute()

    def get_github_teams_syncs(self):
        """Return a list of GithubTeamSync from BITSdb."""
        response = self.bitsdb.github().teams().syncs().list().execute()
        return response.get('items', [])

    # github teams
    def get_github_team(self, team_id):
        """Return a GitHubTeam from BITSdb."""
        return self.bitsdb.github().teams().get(id=team_id).execute()

    def get_github_teams(self, refresh=False):
        """Return a list of GitHubTeams from BITSdb."""
        # key = 'github_teams'
        # github_teams = memcache.get(key)
        # if github_teams is not None and not refresh:
        #     return github_teams
        params = {'limit': 1000}
        github_teams = self.get_paged_list(self.bitsdb.github().teams(), params)
        # memcache.add(key, github_teams, self.memcache_time)
        return github_teams

    # github users
    def get_github_users(self):
        """Return a list of GitHubUsers from BITSdb."""
        # key = 'github_users'
        # github_users = memcache.get(key)
        # if github_users is not None:
        #     return github_users
        params = {'limit': 1000}
        github_users = self.get_paged_list(self.bitsdb.github().users(), params)
        # memcache.add(key, github_users, self.memcache_time)
        return github_users

    # gnarwl responders
    def add_gnarwl(self, body):
        """Add a new Gnarwl Responder to BITSdb."""
        return self.bitsdb.gnarwls().insert(body=body).execute()

    def get_gnarwl(self, username):
        """Get a new GnarwlResponder to BITSdb."""
        return self.bitsdb.gnarwls().get(id=username).execute()

    def get_gnarwls(self):
        """Return a list of Gnarwl entriesfrom BITSdb."""
        # key = 'gnarwls'
        # gnarwls = memcache.get(key)
        # if gnarwls is not None:
        #     return gnarwls
        params = {'limit': 1000}
        gnarwls = self.get_paged_list(self.bitsdb.gnarwls(), params)
        # memcache.add(key, gnarwls, self.memcache_time)
        return gnarwls

    # google billing accounts
    def get_google_billing_accounts(self):
        """Return a list of Google Billing Accounts from BITSdb."""
        # key = 'google_billing_accounts'
        # google_billing_accounts = memcache.get(key)
        # if google_billing_accounts is not None:
        #     return google_billing_accounts
        params = {'limit': 1000}
        google_billing_accounts = self.get_paged_list(self.bitsdb.google().billingaccounts(), params)
        # memcache.add(key, google_billing_accounts, self.memcache_time)
        return google_billing_accounts

    # Google groups
    def get_google_group(self, group_id):
        """Return a GoogleGroup from BITSdb."""
        return self.bitsdb.google().groups().get(id=group_id).execute()

    def get_google_groups(self):
        """Return a list of GoogleGroups from BITSdb."""
        # key = 'google_groups'
        # google_groups = memcache.get(key)
        # if google_groups is not None:
        #     return google_groups
        params = {'limit': 1000}
        google_groups = self.get_paged_list(self.bitsdb.google().groups(), params)
        # memcache.add(key, google_groups, self.memcache_time)
        return google_groups

    # Google users
    def get_google_user(self, user_id):
        """Return a GoogleUser from BITSdb."""
        return self.bitsdb.google().users().get(id=user_id).execute()

    def get_google_users(self):
        """Return a list of GoogleUsers from BITSdb."""
        # key = 'google_users'
        # google_users = memcache.get(key)
        # if google_users is not None:
        #     return google_users
        params = {'limit': 1000}
        google_users = self.get_paged_list(self.bitsdb.google().users(), params)
        # memcache.add(key, google_users, self.memcache_time)
        return google_users

    # hosts
    def get_hosts(self):
        """Return a list of Hosts from BITSdb."""
        # hosts = self.get_memcache_group('hosts')
        # if hosts is not None:
        #     return hosts
        # params = {'limit': 1000}
        # hosts = self.get_paged_list(self.bitsdb.hosts(), params)
        hosts = self.get_datastore_entities('Host')
        # self.save_memcache_group('hosts', hosts, 'name')
        return hosts

    # investigators
    def get_investigators(self):
        """Return a list of Investigators from BITSdb."""
        # key = 'investigators'
        # investigators = memcache.get(key)
        # if investigators is not None:
        #     return investigators
        params = {'limit': 1000}
        investigators = self.get_paged_list(self.bitsdb.investigators(), params)
        # memcache.add(key, investigators, self.memcache_time)
        return investigators

    # isilon
    def get_isilon_quotas(self):
        """Return a IsilonQuotas from BITSdb."""
        # key = 'isilon_quotas'
        # isilon_quotas = memcache.get(key)
        # if isilon_quotas is not None:
        #     return isilon_quotas
        params = {'limit': 1000}
        isilon_quotas = self.get_paged_list(self.bitsdb.isilon().quotas(), params)
        # memcache.add(key, isilon_quotas, self.memcache_time)
        return isilon_quotas

    # newhires
    def get_newhires(self):
        """Return a list of NewHires from BITSdb."""
        # key = 'newhires'
        # newhires = memcache.get(key)
        # if newhires is not None:
        #     return newhires
        params = {'limit': 1000}
        newhires = self.get_paged_list(self.bitsdb.newhires(), params)
        # memcache.add(key, newhires, self.memcache_time)
        return newhires

    # nicknames
    def add_nickname(self, body):
        """Add a new Nickname to BITSdb."""
        return self.bitsdb.nicknames().insert(body=body).execute()

    def get_nickname(self, id):
        """Add a new Nickname to BITSdb."""
        return self.bitsdb.nicknames().get(id=id).execute()

    def get_nicknames(self, cache=True):
        """Return a list of Nicknames from BITSdb."""
        # key = 'nicknames'
        # if cache:
        #     nicknames = memcache.get(key)
        #     if nicknames is not None:
        #         return nicknames
        params = {'limit': 1000}
        nicknames = self.get_paged_list(self.bitsdb.nicknames(), params)
        # memcache.add(key, nicknames, self.memcache_time)
        return nicknames

    # people
    def get_person(self, emplid):
        """Return a person from BITSdb."""
        return self.bitsdb.people().get(id=emplid).execute()

    def get_people(self):
        """Return a list of People from BITSdb."""
        # people = self.get_memcache_group('people')
        # if people is not None:
        #     return people
        # params = {'limit': 1000}
        # people = self.get_paged_list(self.bitsdb.people(), params)
        people = self.get_datastore_entities('Person')
        # self.save_memcache_group('people', people, 'username')
        return people

    # quotes
    def get_quotes(self):
        """Return a list of Quotes from BITSdb."""
        # key = 'quotes'
        # quotes = memcache.get(key)
        # if quotes is not None:
        #     return quotes
        params = {'limit': 1000}
        quotes = self.get_paged_list(self.bitsdb.quotes(), params)
        # memcache.add(key, quotes, self.memcache_time)
        return quotes

    # slack usergroups
    def get_slack_usergroup(self, usergroup_id):
        """Return a SlackUsergroup from BITSdb."""
        return self.bitsdb.slack().usergroups().get(id=usergroup_id).execute()

    def get_slack_usergroups(self):
        """Return a list of SlackUsergroup from BITSdb."""
        # key = 'slack_usergroups'
        # slack_usergroups = memcache.get(key)
        # if slack_usergroups is not None:
        #     return slack_usergroups
        params = {'limit': 1000}
        slack_usergroups = self.get_paged_list(self.bitsdb.slack().usergroups(), params)
        # memcache.add(key, slack_usergroups, self.memcache_time)
        return slack_usergroups

    # slack usergroups
    def add_slack_usergroups_sync(self, body):
        """Add a new SlackUsergroupsSync to BITSdb."""
        return self.bitsdb.slack().usergroups().syncs().insert(body=body).execute()

    def get_slack_usergroups_sync(self, usergroup_id):
        """Return a list of SlackUsergroupsSync from BITSdb."""
        return self.bitsdb.slack().usergroups().syncs().get(id=usergroup_id).execute()

    def get_slack_usergroups_syncs(self):
        """Return a list of SlackUsergroupsSync from BITSdb."""
        response = self.bitsdb.slack().usergroups().syncs().list().execute()
        return response.get('items', [])

    # space
    def get_buildings(self):
        """Return a list of Buildings from BITSdb."""
        # key = 'buildings'
        # buildings = memcache.get(key)
        # if buildings is not None:
        #     return buildings
        params = {'limit': 100}
        buildings = self.get_paged_list(self.bitsdb.buildings(), params)
        # memcache.add(key, buildings, self.memcache_time)
        return buildings

    def get_desks(self):
        """Return a list of Desks from BITSdb."""
        # key = 'desks'
        # desks = memcache.get(key)
        # if desks is not None:
        #     return desks
        params = {'limit': 1000}
        desks = self.get_paged_list(self.bitsdb.desks(), params)
        # memcache.add(key, desks, self.memcache_time)
        return desks

    def get_rooms(self):
        """Return a list of Rooms from BITSdb."""
        # key = 'rooms'
        # rooms = memcache.get(key)
        # if rooms is not None:
        #     return rooms
        params = {'limit': 1000}
        rooms = self.get_paged_list(self.bitsdb.rooms(), params)
        # memcache.add(key, rooms, self.memcache_time)
        return rooms

    def get_seats(self):
        """Return a list of Seats from BITSdb."""
        # key = 'seats'
        # seats = memcache.get(key)
        # if seats is not None:
        #     return seats
        params = {'limit': 1000}
        seats = self.get_paged_list(self.bitsdb.seats(), params)
        # memcache.add(key, seats, self.memcache_time)
        return seats

    # trusted testers
    def add_trustedtester(self, body):
        """Add a new TrustedTester to BITSdb."""
        return self.bitsdb.trustedtesters().insert(body=body).execute()

    def get_trustedtester(self, username):
        """Return an TrustedTester from BITSdb."""
        return self.bitsdb.trustedtesters().get(id=username).execute()

    def get_trustedtesters(self):
        """Return a list of TrustedTesters from BITSdb."""
        # key = 'trustedtesters'
        # trustedtesters = memcache.get(key)
        # if trustedtesters is not None:
        #     return trustedtesters
        params = {'limit': 1000}
        trustedtesters = self.get_paged_list(self.bitsdb.trustedtesters(), params)
        # memcache.add(key, trustedtesters, self.memcache_time)
        return trustedtesters

    # vlans
    def get_vlans(self):
        """Return a list of Vlans from BITSdb."""
        # key = 'vlans'
        # vlans = memcache.get(key)
        # if vlans is not None:
        #     return vlans
        params = {'limit': 1000}
        vlans = self.get_paged_list(self.bitsdb.vlans(), params)
        # memcache.add(key, vlans, self.memcache_time)
        return vlans
