"""Frozen synthetic read-only catalogs and independently specified gold labels."""
APPS = {
 'github':('GitHub',['issues','repositories','pull_requests','commits','discussions','releases','users','projects']),
 'slack':('Slack',['messages','channels','users','files','threads','reactions','bookmarks','canvases']),
 'jira':('Jira',['issues','projects','users','boards','sprints','comments','filters','versions']),
 'gdrive':('Google Drive',['files','folders','documents','spreadsheets','presentations','permissions','comments','shortcuts']),
 'sentry':('Sentry',['events','issues','projects','releases','transactions','traces','alerts','teams']),
 'grafana':('Grafana',['dashboards','datasources','alerts','folders','panels','annotations','teams','users']),
 'pagerduty':('PagerDuty',['incidents','schedules','services','users','teams','escalation_policies','alerts','integrations']),
 'notion':('Notion',['pages','databases','blocks','users','comments','templates','workspaces','collections']),
}


def catalog():
    result=[]
    for app,(title,objects) in APPS.items():
        for obj in objects:
            result.append({'type':'function','function':{
                'name':f'{app}_search_{obj}',
                'description':f'Search {title} {obj.replace("_"," ")}. Read-only. Preserve the quoted query exactly; limit is the maximum result count.',
                'parameters':{'type':'object','properties':{
                    'query':{'type':'string','description':'Exact search text from the user.'},
                    'limit':{'type':'integer','minimum':1,'maximum':20,'description':'Maximum number of results.'}},
                    'required':['query','limit'],'additionalProperties':False}}})
    return sorted(result,key=lambda x:x['function']['name'])


INTENTS=[
 ('github','issues','refresh token',3,'Search GitHub issues','Look for bug reports in the source-code hosting service'),
 ('slack','messages','rollout freeze',5,'Search Slack messages','Find chat posts in our workplace messenger'),
 ('jira','issues','invoice retry',3,'Search Jira issues','Find tickets in our Atlassian issue tracker'),
 ('gdrive','files','architecture review',4,'Search Google Drive files','Locate stored items in our Google cloud storage'),
 ('sentry','events','KeyError',2,'Search Sentry events','Look up captured occurrences in our application error monitoring service'),
 ('grafana','dashboards','service health',3,'Search Grafana dashboards','Locate monitoring overview screens in our observability visualization product'),
 ('pagerduty','schedules','platform primary',2,'Search PagerDuty schedules','Find the on-call rota in our incident-response product'),
 ('notion','pages','onboarding checklist',5,'Search Notion pages','Find wiki entries in our all-in-one workspace app'),
]


def cases():
    result=[]
    for app,obj,query,limit,direct,paraphrase in INTENTS:
        for wording,start in [('explicit',direct),('paraphrase',paraphrase)]:
            result.append({'id':f'{app}-{wording}','intent':app,'wording':wording,
                'request':f'{start} for the exact text "{query}". Return at most {limit} results. Preserve the quoted text verbatim.',
                'expected':{'name':f'{app}_search_{obj}','arguments':{'query':query,'limit':limit}}})
    return result
