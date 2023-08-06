import eons as e
import os
import logging
import platform
import shutil
import jsonpickle
import sqlalchemy as sql
import sqlalchemy.orm as orm
from pathlib import Path
from eot import EOT
import traceback
from subprocess import Popen
from subprocess import PIPE
from subprocess import STDOUT

######## START CONTENT ########
# All Merx errors
class MerxError(Exception): pass

# Exception used for miscellaneous Merx errors.
class OtherMerxError(MerxError): pass


#CatalogCards are classes which will be stored in the catalog.db
SQLBase = orm.declarative_base()

#The Epitome class is an object used for tracking the location, status, and other metadata of a Tome package.
#epi = above, so metadata of a tome would be above a tome, would be epitome. Note that the "tome" portion of epitome actually derives from the word for "to cut". Epitome roughly means an abridgement or surface incision. Abridgement is appropriate here.
#Epitomes should not be extended when creating packages. They are only to be used by Merx for tracking existing packages.
class Epitome(SQLBase):
    __tablename__ = 'tomes'
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String)
    version = sql.Column(sql.String) #not all versions follow Semantic Versioning.
    installed_at = sql.Column(sql.String) #semicolon-separated list of file paths.
    retrieved_from = sql.Column(sql.String) #repo url
    first_retrieved_on = sql.Column(sql.Float) #startdate (per eot).
    last_retrieved_on = sql.Column(sql.Float) #startdate (per eot).
    additional_notes = sql.Column(sql.String) #TODO: Let's convert this to PickleType and store any user-defined values.

    path = None

    def __repr__(this):
        return f"<Epitome(id={this.id}, name={this.name}, version={this.version}, installed_at={this.installed_at}, retrieved_from={this.retrieved_from}, retrieved_on={this.retrieved_on}, additional_notes={this.additional_notes})>"

    def __init__(this, name=None):
        this.name = name


#Transaction logs are recorded whether or not the associated Merx.Transaction() completed.
class TransactionLog(SQLBase):
    __tablename__ = 'transactions'
    id = sql.Column(sql.Integer, primary_key=True)
    when = sql.Column(sql.Float)  #startdate (per eot).
    merx = sql.Column(sql.String) #name of merx
    tomes = sql.Column(sql.String) #semicolon-separated list of tome arguments
    result = sql.Column(sql.Integer) #return value of Merx.DidTransactionSucceed()

    def __init__(this, merx, tomes):
        this.when = EOT.GetStardate()
        this.merx = merx
        this.tomes = tomes

#This is here just to ensure all SQLBase children are created before *this is called.
#TODO: Can we move this into EMI?
def ConstructCatalog(engine):
    SQLBase.metadata.create_all(engine)

#Merx are actions: things like "install", "update", "remove", etc.
#These should be stored on the online repo as merx_{merx.name}, e.g. merx_install, etc.
class Merx(e.UserFunctor):
    def __init__(this, name=e.INVALID_NAME()):
        super().__init__(name)

        this.requiredKWArgs = [
            "tomes", #emi cli arguments 2 and beyond
            "paths", #where to put things, as determined by EMI
        ]
        #executor and catalog are treated specially; see ValidateArgs(), below, for details.

        # For optional args, supply the arg name as well as a default value.
        this.optionalKWArgs = {}

        #args will be provided by EMI.
        this.args = None


    # Do stuff!
    # Override this or die.
    def Transaction(this):
        pass


    # RETURN whether or not the Transaction was successful.
    # Override this to perform whatever success checks are necessary.
    def DidTransactionSucceed(this):
        return False


    # Undo any changes made by Transaction.
    # Please override this too!
    def Rollback(this):
        this.catalog.rollback() #removes all records created by *this (see: https://docs.sqlalchemy.org/en/14/orm/tutorial.html#rolling-back).


    # RETURN whether or not the Transaction was successful.
    # Override this to perform whatever success checks are necessary.
    def DidRollbackSucceed(this):
        return False


    # Hook for any pre-transaction configuration
    def PreTransaction(this):
        pass


    # Hook for any post-transaction configuration
    def PostTransaction(this):
        pass
    

    # Convert Fetched values to their proper type.
    # This can also allow for use of {this.val} expression evaluation.
    def EvaluateToType(this, value, evaluateExpression = False):
        if (isinstance(value, dict)):
            ret = {}
            for key, value in value.items():
                ret[key] = this.EvaluateToType(value)
            return ret

        elif (isinstance(value, list)):
            ret = []
            for value in value:
                ret.append(this.EvaluateToType(value))
            return ret

        else:
            if (evaluateExpression):
                evaluatedvalue = eval(f"f\"{value}\"")
            else:
                evaluatedvalue = str(value)

            #Check original type and return the proper value.
            if (isinstance(value, (bool, int, float)) and evaluatedvalue == str(value)):
                return value

            #Check resulting type and return a casted value.
            #TODO: is there a better way than double cast + comparison?
            if (evaluatedvalue.lower() == "false"):
                return False
            elif (evaluatedvalue.lower() == "true"):
                return True

            try:
                if (str(float(evaluatedvalue)) == evaluatedvalue):
                    return float(evaluatedvalue)
            except:
                pass

            try:
                if (str(int(evaluatedvalue)) == evaluatedvalue):
                    return int(evaluatedvalue)
            except:
                pass

            #The type must be a string.
            return evaluatedvalue


    # Wrapper around setattr
    def Set(this, varName, value):
        value = this.EvaluateToType(value)
        logging.debug(f"Setting ({type(value)}) {varName} = {value}")
        setattr(this, varName, value)


    # Will try to get a value for the given varName from:
    #    first: this
    #    second: the executor (args > config > environment)
    # RETURNS the value of the given variable or None.
    def Fetch(this,
        varName,
        default=None,
        enableThisMerx=True,
        enableThisExecutor=True,
        enableExecutorConfig=True,
        enableEnvironment=True):

        ret = this.executor.Fetch(varName, default, enableThisExecutor, False, enableExecutorConfig, enableEnvironment)

        if (enableThisMerx and hasattr(this, varName)):
            logging.debug(f"...got {varName} from self ({this.name}).")
            return getattr(this, varName)

        return ret


    # Override of eons.UserFunctor method. See that class for details.
    def ValidateArgs(this, **kwargs):
        # logging.debug(f"Got arguments: {kwargs}")
        setattr(this, 'executor', kwargs['executor'])
        setattr(this, 'catalog', kwargs['catalog'])

        for rkw in this.requiredKWArgs:
            if (hasattr(this, rkw)):
                continue

            if (rkw in kwargs):
                this.Set(rkw, kwargs[rkw])
                continue

            fetched = this.Fetch(rkw)
            if (fetched is not None):
                this.Set(rkw, fetched)
                continue

            # Nope. Failed.
            errStr = f"{rkw} required but not found."
            logging.error(errStr)
            raise MerxError(errStr)

        for okw, default in this.optionalKWArgs.items():
            if (hasattr(this, okw)):
                continue

            if (okw in kwargs):
                this.Set(okw, kwargs[okw])
                continue

            this.Set(okw, this.Fetch(okw, default=default))


    # Override of eons.Functor method. See that class for details
    def UserFunction(this, **kwargs):
        logging.info(f"Initiating Transaction {this.name} for {this.args}")

        this.PreTransaction()

        logging.debug(f"<---- {this.name} ---->")
        this.Transaction()
        logging.debug(f">----<")

        this.PostTransaction()

        if (this.DidTransactionSucceed()):
            logging.debug("Success :)")
        else:
            logging.error("Transaction did not succeed :(")


    # Open or download a Tome.
    # tomeName should be given without the "tome_" prefix
    # RETURNS an Epitome containing the given Tome's Path and details or None.
    def GetTome(this, tomeName):
        return this.executor.GetTome(tomeName)

    # RETURNS: an opened file object for writing.
    # Creates the path if it does not exist.
    def CreateFile(this, file, mode="w+"):
        Path(os.path.dirname(os.path.abspath(file))).mkdir(parents=True, exist_ok=True)
        return open(file, mode)


    # Run whatever.
    # DANGEROUS!!!!!
    # TODO: check return value and raise exceptions?
    # per https://stackoverflow.com/questions/803265/getting-realtime-output-using-subprocess
    def RunCommand(this, command):
        p = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
        while True:
            line = p.stdout.readline()
            if (not line):
                break
            print(line.decode('utf8')[:-1])  # [:-1] to strip excessive new lines.


class PathSelector:
    def __init__(this, name, systemPath):
        this.name = name
        this.systemPath = systemPath
        this.selectedPath = None

class EMI(e.Executor):

    def __init__(this):

        # The library is where all Tomes are initially distributed from (i.e. the repo_store)
        #   and where records for all Tome locations and Merx Transactions are kept.
        # We need to create these files for there to be a valid config.json to read from. Otherwise, eons.Executor crashes.
        this.library = Path.home().joinpath(".eons")
        this.sqlEngine = sql.create_engine(f"sqlite:///{str(this.library.joinpath('catalog.db'))}")
        this.catalog = orm.sessionmaker(bind=this.sqlEngine)() #sqlalchemy: sessionmaker()->Session()->session.
        this.SetupHome()

        super().__init__(name="eons Modular Installer", descriptionStr="A universal package manager.")

        #Windows paths must be set in the config.json.
        this.paths = [
            PathSelector("bin", "/usr/local/bin/"),
            PathSelector("inc", "/usr/local/include/"),
            PathSelector("lib", "/usr/local/lib/")
        ]

    #Create initial resources if they don't already exist.
    def SetupHome(this):
        if (not this.library.exists()):
            logging.info(f"Creating home folder: {str(this.library)}")
            this.library.mkdir()
            this.library.joinpath("tmp").mkdir()

        catalogFile = this.library.joinpath("catalog.db")
        if (not catalogFile.exists()):
            logging.info(f"Creating catalog: {str(catalogFile)}")
            catalogFile.touch()
        if (not catalogFile.stat().st_size):
            logging.info("Constructing catalog scheme")
            ConstructCatalog(this.sqlEngine)

        configFile = this.library.joinpath("config.json")
        if (not configFile.exists() or not configFile.stat().st_size):
            logging.info(f"Initializing config file: {str(configFile)}")
            config = open(configFile, "w+")
            config.write("{\n}")


    #Override of eons.Executor method. See that class for details
    def Configure(this):
        super().Configure()
        this.tomeDirectory = this.library.joinpath("tmp")
        this.defaultRepoDirectory = str(this.library.joinpath("merx"))
        this.defualtConfigFile = str(this.library.joinpath("config.json"))

    #Override of eons.Executor method. See that class for details
    def RegisterAllClasses(this):
        super().RegisterAllClasses()

    #Override of eons.Executor method. See that class for details
    def AddArgs(this):
        super().AddArgs()
        this.argparser.add_argument('merx', type=str, metavar='merx', help='what to do (e.g. \'install\' or \'remove\')')
        this.argparser.add_argument('tomes', type=str, nargs='*', metavar='tome', help='how to do it (e.g. \'my_package\')')

    #Override of eons.Executor method. See that class for details
    def ParseArgs(this):
        super().ParseArgs()
        #NOTE: THERE SHOULD BE NO this.extraArgs

    #Override of eons.Executor method. See that class for details
    def UserFunction(this, **kwargs):

        super().UserFunction(**kwargs)
        
        #paths will be provided to the Merx as a dictionary.
        this.SelectPaths()
        paths = {}
        for path in this.paths:
            paths[path.name] = path.selectedPath

        transaction = TransactionLog(this.args.merx, '; '.join(this.args.tomes))
        try:
            merx = this.GetRegistered(this.args.merx, "merx")
            merx(executor=this, tomes=this.args.tomes, paths=paths, catalog=this.catalog)
            if (merx.DidTransactionSucceed()):
                transaction.result = 0
                logging.info(f"Complete.")
            else:
                logging.warning(f"Transaction failed. Attempting Rollback...")
                merx.Rollback()
                if (merx.DidRollbackSucceed()):
                    transaction.result = 1
                    logging.info(f"Rollback succeeded. All is well.")
                else:
                    transaction.result = 2
                    logging.error(f"Rollback FAILED! SYSTEM STATE UNKNOWN!!!")
        except Exception as error:
            transaction.result = False
            logging.error(f"ERROR: {error}")
            traceback.print_exc()
        this.catalog.add(transaction)
        this.catalog.commit() #make sure the transaction log gets committed.

        #TODO: develop TransactionLog retention policy (i.e. trim records after 1 year, 1 day, or don't record at all).

    def SelectPaths(this):
        for path in this.paths:
            preferredPath = Path(this.Fetch(f"{path.name}_path", default=path.systemPath))
            if (preferredPath.exists() and os.access(str(preferredPath), os.W_OK | os.X_OK)):
                path.selectedPath = preferredPath
            else:
                path.selectedPath = this.library.joinpath(path.name)
                logging.debug(f"The preferred path for {path.name} ({str(preferredPath)}) was unusable.")
                path.selectedPath.mkdir(exist_ok=True)
            logging.debug(f"Path for {path.name} set to {str(path.selectedPath)}.")

    # GetRegistered modified for use with Tomes.
    # tomeName should be given without the "tome_" prefix
    # RETURNS an Epitome containing the given Tome's Path and details or None.
    def GetTome(this, tomeName):
        logging.debug(f"Fetching tome_{tomeName}.")

        tomePath = this.tomeDirectory.joinpath(f"tome_{tomeName}")
        logging.debug(f"Will place {tomeName} in {tomePath}.")

        epitome = this.catalog.query(Epitome).filter(Epitome.name==tomeName).first()
        if (epitome is None):
            epitome = Epitome(tomeName)
        else:
            logging.debug(f"Got exiting Epitome for {tomeName}.")

        if (tomePath.exists()):
            logging.debug(f"Found {tomeName} on the local filesystem.")
            epitome.path = tomePath
        else:
            preservedRepo = this.repo['store']
            preservedUrl = this.repo['url']
            if (epitome.retrieved_from is not None and len(epitome.retrieved_from)):
                this.repo['url'] = epitome.retrieved_from
            this.repo['store'] = str(this.tomeDirectory)
            logging.debug(f"Attempting to download {tomeName} from {this.repo['url']}")
            this.DownloadPackage(packageName=f"tome_{tomeName}", registerClasses=False, createSubDirectory=True)
            if (tomePath.exists()):
                epitome.path = tomePath
                epitome.retrieved_from = this.repo['url']
                if (epitome.first_retrieved_on is None or epitome.first_retrieved_on == 0):
                    epitome.first_retrieved_on = EOT.GetStardate()
                epitome.last_retrieved_on = EOT.GetStardate()
                if (epitome.version is None):
                    epitome.version = ""
                    # TODO: populate epitome.version. Blocked by https://github.com/infrastructure-tech/srv_infrastructure/issues/2
            else:
                logging.error(f"Failed to download tome_{tomeName}")

            this.repo['url'] = preservedUrl
            this.repo['store'] = preservedRepo

        return epitome

