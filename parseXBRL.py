from bs4 import BeautifulSoup
import re
from xbrlOptions import xbrlOptions


def findUsGaap(xbrl, optionsArray, contextArray):
    for option in optionsArray:
        try:
            result = xbrl.find(re.compile('(us-gaap:'+option+')', re.IGNORECASE | re.MULTILINE), {
                'contextref': re.compile('({})|({})'.format(contextArray[0], contextArray[1]))}).text

            if result:
                if not result.isdigit():
                    continue
            return result

        except Exception as e:
            pass

    return 0


def findDei(xbrl, optionsArray):
    for option in optionsArray:
        try:
            if isinstance(option, dict):
                for key, val in option.items():
                    result = xbrl.find(re.compile(
                        'dei:'+key, re.IGNORECASE | re.MULTILINE))[val]
            else:
                result = xbrl.find(re.compile(
                    'dei:'+option, re.IGNORECASE | re.MULTILINE)).text

            if result:
                return result
        except Exception as e:
            pass

    return False


def parseXbrl(file):
    company = {}
    xbrl = BeautifulSoup(open(file), 'lxml')

    for key, val in xbrlOptions['dei'].items():
        company[key] = findDei(xbrl, val)

    # Must be able to get contextref to proceed
    if company['DocumentFiscalYearFocusContext']:
        context = company['DocumentFiscalYearFocusContext'][:8].replace(
            'D', 'I')
        company['ContextForInstants'] = context

        ctx = company['ContextForInstants']
        ctx2 = company['DocumentFiscalPeriodFocusContext']
        contextArray = [ctx, ctx2]

        for key, val in xbrlOptions['us-gaap'].items():
            ctx = company['ContextForInstants']
            ctx2 = company['DocumentFiscalPeriodFocusContext']
            contextArray = [ctx, ctx2]
            company[key] = findUsGaap(xbrl, val, contextArray)
    else:
        print('Cannot Find Context Ref')

    try:
        company['ROA'] = (float(company['NetIncomeLoss']) /
                          float(company['Assets']))
    except Exception as e:
        company['ROA'] = e

    try:
        NetAssets = (float(company['Assets']) - float(company['Liabilities']))

        company['ROE'] = (float(company['NetIncomeLoss']) / (NetAssets))
    except Exception as e:
        company['ROE'] = e

    try:
        company['ROS'] = (float(company['NetIncomeLoss']) /
                          float(company['Revenues']))
    except Exception as e:
        company['ROS'] = e

    try:
        company['SGR'] = (company['ROE'] * (1 -
                                            (float(company['Dividends']) / float(company['NetIncomeLoss']))))
    except Exception as e:
        company['SGR'] = e

    try:
        company['DE'] = (float(company['Liabilities']) /
                         float(company['Equity']))
    except Exception as e:
        company['DE'] = e

    try:
        company['BookValue'] = ((float(company['Assets']) -
                                 float(company['Liabilities'])) / float(company['OutstandingShares']))
    except Exception as e:
        company['BookValue'] = e

    return company


FILE = 'testData/aapl-2018-11-05.xml'

result = parseXbrl(FILE)
print(result)
