========================
PyAMS SQLAlchemy package
========================

Introduction
------------

This package is composed of a set of utility functions, usable into any Pyramid application.

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)
    >>> config.registry.settings['zodbconn.uri'] = 'memory://'
    >>> config.registry.settings['pyams_alchemy.cleaner.timeout'] = 'off'

    >>> from pyramid_zodbconn import includeme as include_zodbconn
    >>> include_zodbconn(config)
    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)
    >>> from pyams_site import includeme as include_site
    >>> include_site(config)
    >>> from pyams_security import includeme as include_security
    >>> include_security(config)
    >>> from pyams_skin import includeme as include_skin
    >>> include_skin(config)
    >>> from pyams_zmi import includeme as include_zmi
    >>> include_zmi(config)
    >>> from pyams_form import includeme as include_form
    >>> include_form(config)
    >>> from pyams_zmq import includeme as include_zmq
    >>> include_zmq(config)
    >>> from pyams_scheduler import includeme as include_scheduler
    >>> include_scheduler(config)
    >>> from pyams_alchemy import includeme as include_alchemy
    >>> include_alchemy(config)

    >>> from pyams_site.generations import upgrade_site
    >>> request = DummyRequest()
    >>> app = upgrade_site(request)
    Upgrading PyAMS timezone to generation 1...
    Upgrading PyAMS security to generation 2...
    Upgrading PyAMS scheduler to generation 1...
    Upgrading PyAMS alchemy to generation 1...

    >>> from pyams_utils.registry import set_local_registry
    >>> set_local_registry(app.getSiteManager())


Creating an SQLAlchemy engine
-----------------------------

An SQLAlchemy engine can be defined as a persistent utility:

    >>> from pyams_utils.factory import get_object_factory
    >>> from pyams_utils.registry import get_utility
    >>> from pyams_alchemy.interfaces import IAlchemyManager, IAlchemyEngineUtility

    >>> sm = get_utility(IAlchemyManager)
    >>> sm
    <pyams_alchemy.manager.AlchemyManager object at 0x... oid 0x... in <Connection at ...>>

    >>> factory = get_object_factory(IAlchemyEngineUtility)
    >>> engine = factory()
    >>> engine
    <pyams_alchemy.engine.PersistentAlchemyEngineUtility object at 0x...>
    >>> engine.name = 'MY_SESSION'
    >>> engine.dsn = 'sqlite://'

    >>> sm['SESSION'] = engine

    >>> from zope.lifecycleevent import ObjectAddedEvent
    >>> request.registry.notify(ObjectAddedEvent(engine, sm))

    >>> get_utility(IAlchemyEngineUtility, name='MY_SESSION') is engine
    True

We can now try to get a SQLAlchemy session from our registered utility:

    >>> from pyams_alchemy.engine import get_user_session
    >>> session = get_user_session('MY_SESSION', twophase=False)
    >>> session
    <sqlalchemy.orm.session.Session object at 0x...>

    >>> import transaction
    >>> results = list(session.execute('select date()'))
    >>> len(results)
    1
    >>> results[0][0]
    '...-...-...'


SQLAlchemy tasks
----------------

PyAMS_alchemy provides a PyAMS_scheduler task which can be used to execute SQL instructions
as scheduled tasks:

    >>> from pyams_alchemy.task.interfaces import IAlchemyTask
    >>> factory = get_object_factory(IAlchemyTask)

    >>> task = factory()
    >>> task.session_name = 'MY_SESSION'
    >>> task.query = 'select date() as now'

    >>> from io import StringIO
    >>> report = StringIO()

    >>> status, result = task.run(report)
    >>> status
    'OK'
    >>> result
    '[{"now": "...-...-..."}]'

Task output can also be defined in CSV format:

    >>> task.output_format = 'csv'
    >>> status, result = task.run(report)
    >>> print(result)
    now
    ...-...-...

    >>> task.output_format = 'json'


We can create tasks which doesn't return any result:

    >>> report = StringIO()
    >>> task.query = 'create table TEST1 (id integer)'
    >>> status, result = task.run(report)
    >>> status
    'empty'
    >>> result is None
    True

    >>> _ = report.seek(0)
    >>> print(report.read())
    SQL query output
    ================
    SQL query:
        create table TEST1 (id integer)
    SQL query returned no result.

Tasks should also handle SQL errors correctly:

    >>> report = StringIO()
    >>> task.query = 'select * from MISSING_TABLE'
    >>> status, result = task.run(report)
    >>> status
    'fail'
    >>> result is None
    True

    >>> _ = report.seek(0)
    >>> print(report.read())
    SQL query output
    ================
    SQL query:
        select * from MISSING_TABLE
    An SQL error occurred
    =====================
    Traceback (most recent call last):
    ...
    sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: MISSING_TABLE
    [SQL: select * from MISSING_TABLE]
    (Background on this error at: http://sqlalche.me/...)


Tests cleanup:

    >>> tearDown()
