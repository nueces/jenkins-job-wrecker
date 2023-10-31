# encoding=utf8
import jenkins_job_wrecker.modules.base
from jenkins_job_wrecker.helpers import get_bool, gen_raw


class Builders(jenkins_job_wrecker.modules.base.Base):
    component = 'builders'

    def gen_yml(self, yml_parent, data):
        builders = []
        for child in data:
            object_name = child.tag.split('.')[-1].lower()
            self.registry.dispatch(self.component, object_name, child, builders)
        yml_parent.append(['builders', builders])


def copyartifact(child, parent):
    copyartifact = {}
    selectdict = {
        'StatusBuildSelector': 'last-successful',
        'LastCompletedBuildSelector': 'last-completed',
        'SpecificBuildSelector': 'specific-build',
        'SavedBuildSelector': 'last-saved',
        'TriggeredBuildSelector': 'upstream-build',
        'PermalinkBuildSelector': 'permalink',
        'WorkspaceSelector': 'workspace-latest',
        'ParameterizedBuildSelector': 'build-param',
        'DownstreamBuildSelector': 'downstream-build'}
    for copy_element in child:
        if copy_element.tag == 'project':
            copyartifact[copy_element.tag] = copy_element.text
        elif copy_element.tag == 'filter':
            copyartifact[copy_element.tag] = copy_element.text
        elif copy_element.tag == 'target':
            copyartifact[copy_element.tag] = copy_element.text
        elif copy_element.tag == 'excludes':
            copyartifact['exclude-pattern'] = copy_element.text
        elif copy_element.tag == 'selector':
            select = copy_element.attrib['class']
            select = select.replace('hudson.plugins.copyartifact.', '')
            copyartifact['which-build'] = selectdict[select]
        elif copy_element.tag == 'flatten':
            copyartifact[copy_element.tag] = \
                (copy_element.text == 'true')
        elif copy_element.tag == 'doNotFingerprintArtifacts':
            # Not yet implemented in JJB
            # ADD RAW XML
            continue
        elif copy_element.tag == 'optional':
            copyartifact[copy_element.tag] = \
                (copy_element.text == 'true')
        else:
            raise NotImplementedError("cannot handle "
                                      "XML %s" % copy_element.tag)

    parent.append({'copyartifact': copyartifact})


def maven(child, parent):
    maven = {}
    for maven_element in child:
        if maven_element.tag == 'targets':
            maven['goals'] = maven_element.text
        elif maven_element.tag == 'mavenName':
            maven['name'] = maven_element.text
        elif maven_element.tag == 'usePrivateRepository':
            maven['private-repository'] = (maven_element.text == 'true')
        elif maven_element.tag == 'settings':
            maven['settings'] = maven_element.attrib['class']
        elif maven_element.tag == 'globalSettings':
            maven['global-settings'] = maven_element.attrib['class']
        else:
            continue

    parent.append({'maven-target': maven})


def shell(child, parent):
    shell = ''
    for shell_element in child:
        # Assumption: there's only one <command> in this
        # <hudson.tasks.Shell>
        if shell_element.tag == 'command':
            if shell_element.text is not None:
                shell = shell_element.text
        else:
            raise NotImplementedError("cannot handle "
                                      "XML %s" % shell_element.tag)

    parent.append({'shell': shell})


def batchfile(child, parent):
    shell = ''
    for shell_element in child:
        # Assumption: there's only one <command> in this
        # <hudson.tasks.Shell>
        if shell_element.tag == 'command':
            if shell_element.text is not None:
                shell = str(shell_element.text)
        else:
            raise NotImplementedError("cannot handle "
                                      "XML %s" % shell_element.tag)

    parent.append({'batch': shell})


def buildnameupdater(child, parent):
    build_name = {}
    for build_name_element in child:
        if build_name_element.tag == "buildName":
            build_name["name"] = build_name_element.text
        elif build_name_element.tag == "macroTemplate":
            build_name["template"] = build_name_element.text
        elif build_name_element.tag == "fromFile":
            build_name["file"] = (build_name_element.text == 'true')
        elif build_name_element.tag == "fromMacro":
            build_name["macro"] = (build_name_element.text == 'true')
        elif build_name_element.tag == "macroFirst":
            build_name["macro-first"] = (build_name_element.text == 'true')
        else:
            raise NotImplementedError("cannot handle "
                                      "XML %s" % build_name_element.tag)

    parent.append({'build-name-setter': build_name})


def multijobbuilder(child, parent):
    multijob = {}
    for element in child:
        if element.tag == "phaseName":
            multijob["name"] = element.text
        elif element.tag == "continuationCondition":
            multijob["condition"] = element.text
        elif element.tag == "executionType":
            multijob["execution-type"] = element.text
        elif element.tag == "phaseJobs":
            multijob['projects'] = []
            for p_element in element:
                config = {}
                for cfg_element in p_element:
                    if cfg_element.tag == 'jobName':
                        config['name'] = cfg_element.text
                    elif cfg_element.tag == 'jobAlias':
                        if cfg_element.text:
                            config['alias'] = cfg_element.text
                    elif cfg_element.tag == 'currParams':
                        config['current-parameters'] = get_bool(cfg_element.text)
                    elif cfg_element.tag == 'aggregatedTestResults':
                        config['aggregated-test-results'] = get_bool(cfg_element.text)
                    elif cfg_element.tag == 'exposedSCM':
                        config['exposed-scm'] = cfg_element.text
                    elif cfg_element.tag == 'disableJob':
                        config['disable-job'] = get_bool(cfg_element.text)
                    elif cfg_element.tag == 'parsingRulesPath':
                        if cfg_element.text:
                            config['parsing-rule-path'] = cfg_element.text
                    elif cfg_element.tag == 'maxRetries':
                        config['max-retries'] = int(cfg_element.text)
                    elif cfg_element.tag == 'enableRetryStrategy':
                        config['enable-retry-strategy'] = get_bool(cfg_element.text)
                    elif cfg_element.tag == 'enableCondition':
                        config['enable-condition'] = get_bool(cfg_element.text)
                    elif cfg_element.tag == 'abortAllJob':
                        config['abort-all-job'] = get_bool(cfg_element.text)
                    elif cfg_element.tag == 'condition':
                        if cfg_element.text:
                            config['condition'] = cfg_element.text
                    elif cfg_element.tag == 'configs':
                        config['configs'] = []
                        gen_raw(element, config['configs'])
                    elif cfg_element.tag == 'killPhaseOnJobResultCondition':
                        config['kill-phase-on-job-result-condition'] = cfg_element.text
                    elif cfg_element.tag == 'buildOnlyIfSCMChanges':
                        config['build-only-if-scm-change'] = get_bool(cfg_element.text)
                    elif cfg_element.tag == 'applyConditionOnlyIfNoSCMChanges':
                        config['apply-condition-only-of-no-scm-change'] = get_bool(cfg_element.text)
                    else:
                        raise NotImplementedError("cannot handle XML %s" % cfg_element.tag)

                multijob['projects'].append(config)
        else:
            raise NotImplementedError("cannot handle XML %s" % element.tag)

    parent.append({'multijob': multijob})
