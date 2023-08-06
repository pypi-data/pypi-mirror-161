//=============================================================================
/* ����ʢͳһ����API�ӿ�
 * ���ļ�������EsTradeAPI ʹ�õ���������
 * �汾��Ϣ:2018-05-21 ������ �������ļ�
 */
//=============================================================================
#ifndef ES_TRADE_API_DATA_TYPE_H
#define ES_TRADE_API_DATA_TYPE_H
namespace EsTradeAPI
{
#pragma pack(push, 1)

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_CHARS    �����ַ������Ͷ���
     *    @{
     */
     //=============================================================================
    //! ���ַ�
    typedef char                    TAPICHAR;
    //! ����Ϊ10���ַ���
    typedef char                    TAPISTR_10[11];
    //! ����Ϊ20���ַ���
    typedef char                    TAPISTR_20[21];
    //! ����Ϊ30���ַ���
    typedef char                    TAPISTR_30[31];
    //! ����Ϊ40���ַ���
    typedef char                    TAPISTR_40[41];
    //! ����Ϊ50���ַ���
    typedef char                    TAPISTR_50[51];
    //! ����Ϊ70���ַ���
    typedef char                    TAPISTR_70[71];
    //! ����Ϊ100���ַ���
    typedef char                    TAPISTR_100[101];
    //! ����Ϊ200���ַ���
    typedef char                    TAPISTR_200[201];
    //! ����Ϊ300���ַ���
    typedef char                    TAPISTR_300[301];
    //! ����Ϊ500���ַ���
    typedef char                    TAPISTR_500[501];
    //! ����Ϊ2000���ַ���
    typedef char                    TAPISTR_2000[2001];
    //! ����Ϊ512����֤���ַ���Authorization Code
    typedef char                    TAPIAUTHCODE[513];
    //! ������֤���
    typedef char                    TAPISecondSerialIDType[5];
    //! ��¼Mac����
    typedef char                    TAPIMacType[13];
    //! ���˻�����
    typedef char                    TAPIClientIDType[16];

    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_NUMBER    ������ֵ���Ͷ���
     *    @{
     */
     //=============================================================================
     //! int 32
    typedef int                        TAPIINT32;
    //! unsigned 32
    typedef unsigned int            TAPIUINT32;
    //! int 64
    typedef long long                TAPIINT64;
    //! unsigned 64
    typedef unsigned long long        TAPIUINT64;
    //! unsigned 16
    typedef unsigned short            TAPIUINT16;
    //! unsigned 8
    typedef unsigned char            TAPIUINT8;
    //! real 64
    typedef double                    TAPIREAL64;
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_YNFLAG    �Ƿ��ʾ
     *    @{
     */
     //=============================================================================
    //! �Ƿ��ʾ
    typedef TAPICHAR                TAPIYNFLAG;
    //! ��
    const TAPIYNFLAG                APIYNFLAG_YES = 'Y';
    //! ��
    const TAPIYNFLAG                APIYNFLAG_NO = 'N';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_DATETIME    ����ʱ�����Ͷ���
     *    @{
     */
     //=============================================================================
    //! ʱ�������
    typedef char                    TAPIDTSTAMP[24];
    //! ���ں�ʱ������
    typedef char                    TAPIDATETIME[20];
    //! ��������
    typedef char                    TAPIDATE[11];
    //! ʱ������
    typedef char                    TAPITIME[9];
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_LOG_LEVEL    ��־����
     *    @{
     */
     //=============================================================================
     //! ��־����
    typedef TAPICHAR                TAPILOGLEVEL;
    //! Error
    const TAPILOGLEVEL                APILOGLEVEL_ERROR = '1';
    //! Normal
    const TAPILOGLEVEL                APILOGLEVEL_NORMAL = '2';
    //! Debug
    const TAPILOGLEVEL                APILOGLEVEL_DEBUG = '3';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_COMMODITY_TYPE    Ʒ������
     *    @{
     */
     //=============================================================================
     //! Ʒ������
    typedef TAPICHAR                TAPICommodityType;
    //! ��
    const TAPICommodityType            TAPI_COMMODITY_TYPE_NONE = 'N';
    //! �ֻ�
    const TAPICommodityType            TAPI_COMMODITY_TYPE_SPOT = 'P';
    //! �ڻ�
    const TAPICommodityType            TAPI_COMMODITY_TYPE_FUTURES = 'F';
    //! ��Ȩ
    const TAPICommodityType            TAPI_COMMODITY_TYPE_OPTION = 'O';
    //! ��������
    const TAPICommodityType            TAPI_COMMODITY_TYPE_SPREAD_MONTH = 'S';
    //! ��Ʒ������
    const TAPICommodityType            TAPI_COMMODITY_TYPE_SPREAD_COMMODITY = 'M';
    //! ���Ǵ�ֱ����
    const TAPICommodityType            TAPI_COMMODITY_TYPE_BUL = 'U';
    //! ������ֱ����
    const TAPICommodityType            TAPI_COMMODITY_TYPE_BER = 'E';
    //! ��ʽ����
    const TAPICommodityType            TAPI_COMMODITY_TYPE_STD = 'D';
    //! ���ʽ����
    const TAPICommodityType            TAPI_COMMODITY_TYPE_STG = 'G';
    //! �������
    const TAPICommodityType            TAPI_COMMODITY_TYPE_PRT = 'R';
    //! ����ˮƽ��Ȩ
    const TAPICommodityType            TAPI_COMMODITY_TYPE_BLT = 'L';
    //! ����ˮƽ��Ȩ
    const TAPICommodityType           TAPI_COMMODITY_TYPE_BRT = 'Q';
    //! ��㡪ֱ�ӻ���
    const TAPICommodityType            TAPI_COMMODITY_TYPE_DIRECTFOREX = 'X';
    //! ��㡪��ӻ���
    const TAPICommodityType            TAPI_COMMODITY_TYPE_INDIRECTFOREX = 'I';
    //! ��㡪�������
    const TAPICommodityType            TAPI_COMMODITY_TYPE_CROSSFOREX = 'C';
    //! ָ��
    const TAPICommodityType            TAPI_COMMODITY_TYPE_INDEX = 'Z';
    //! ��Ʊ
    const TAPICommodityType            TAPI_COMMODITY_TYPE_STOCK = 'T';
    //! �ֻ�����
    const TAPICommodityType            TAPI_COMMODITY_TYPE_SPOT_TRADINGDEFER = 'Y';
    //! �������
    const TAPICommodityType            TAPI_COMMODITY_TYPE_FUTURE_LOCK = 'J';
    //! �н�����ͬ�·ݿ�Ʒ������
    const TAPICommodityType            TAPI_COMMODITY_TYPE_SPREAD_C_COMMODITY = 'K';
    //! �н���EFP
    const TAPICommodityType            TAPI_COMMODITY_TYPE_EFP = 'A';
    //! TAS�����Ʒ��
    const TAPICommodityType         TAPI_COMMODITY_TYPE_TAS = 'B';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_CALL_OR_PUT    ���ǿ�����ʾ
     *    @{
     */
     //=============================================================================
     //! ���ǿ�����ʾ
    typedef TAPICHAR                TAPICallOrPutFlagType;
    //! ��Ȩ
    const TAPICallOrPutFlagType        TAPI_CALLPUT_FLAG_CALL = 'C';
    //! ��Ȩ
    const TAPICallOrPutFlagType        TAPI_CALLPUT_FLAG_PUT = 'P';
    //! ��
    const TAPICallOrPutFlagType        TAPI_CALLPUT_FLAG_NONE = 'N';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIACCOUNTTYPE    �˺�����
     *    @{
     */
     //=============================================================================
     //! �˺�����
    typedef TAPICHAR                TAPIAccountType;
    //! ���˿ͻ�
    const TAPIAccountType            TAPI_ACCOUNT_TYPE_PERSON = 'P';
    //! �����ͻ�
    const TAPIAccountType            TAPI_ACCOUNT_TYPE_ORGANIZATION = 'O';
    //! ������
    const TAPIAccountType            TAPI_ACCOUNT_TYPE_AGENT = 'A';
    //! Margin
    const TAPIAccountType            TAPI_ACCOUNT_TYPE_MARGIN = 'M';
    //! Internal
    const TAPIAccountType            TAPI_ACCOUNT_TYPE_INTERNAL = 'I';
    //! House
    const TAPIAccountType            TAPI_ACCOUNT_TYPE_HOUSE = 'H';
    //! ��Ʊ�˻�
    const TAPIAccountType            TAPI_ACCOUNT_TYPE_STOCK = 'S';
    //! ������
    const TAPIAccountType            TAPI_ACCOUNT_TYPE_MARTKET = 'R';
    //! GiveUp�ͻ�
    const TAPIAccountType            TAPI_ACCOUNT_TYPE_GIVEUP = 'G';
    //! ���˻�
    const TAPIAccountType            TAPI_ACCOUNT_TYPE_ERRACCOUNT = 'E';
    /** @}*/

    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_T_TAPIRIGHTIDTYPE    Ȩ�ޱ�������
    *    @{
    */
    //=============================================================================
    //! Ȩ�ޱ�������
    typedef TAPIINT32                TAPIRightIDType;
    //! ϵͳɾ��
    const TAPIRightIDType            TAPI_RIGHT_ORDER_DEL = 30001;
    //! �������
    const TAPIRightIDType            TAPI_RIGHT_ORDER_CHECK = 30002;
    //! ���ӵ��޸ġ�ɾ��(��)
    const TAPIRightIDType            TAPI_RIGHT_ORDER_MODIFY = 30003;
    //! ����ת�ơ��ɽ�ת��(��)
    const TAPIRightIDType            TAPI_RIGHT_ORDER_TRANFER = 30004;
    //! ����¼��(��)
    const TAPIRightIDType            TAPI_RIGHT_ORDER_INPUT = 30005;
    //! ֻ�ɲ�ѯ
    const TAPIRightIDType            TAPI_RIGHT_ONLY_QRY = 31000;
    //! ֻ�ɿ���
    const TAPIRightIDType            TAPI_RIGHT_ONLY_OPEN = 31001;
    //! ���ڲ�ҵ�
    const TAPIRightIDType            TAPI_RIGHT_SHFE_QUOTE = 31002;
    //! ֻ��ƽ��Ȩ��
    const TAPIRightIDType            TAPI_RIGHT_ONLY_COVER = 31003;
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIUSERTYPETYPE    ��¼�û��������
     *    @{
     */
     //=============================================================================
     //! ��¼�û��������
    typedef TAPIINT32                TAPIUserTypeType;
    //! Ͷ�����û�
    const TAPIUserTypeType            TAPI_USERTYPE_CLIENT = 10000;
    //! ������
    const TAPIUserTypeType            TAPI_USERTYPE_BROKER = 20000;
    //! ����Ա
    const TAPIUserTypeType            TAPI_USERTYPE_TRADER = 30000;
    //! ���Ա
    const TAPIUserTypeType            TAPI_USERTYPE_RISK = 40000;
    //! ����Ա
    const TAPIUserTypeType            TAPI_USERTYPE_MANAGER = 50000;
    //! ����
    const TAPIUserTypeType            TAPI_USERTYPE_QUOTE = 60000;
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIACCOUNTSTATE    �˺�״̬
     *    @{
     */
     //=============================================================================
     //! �˺�״̬
    typedef TAPICHAR                TAPIAccountState;
    //! ����
    const TAPIAccountState            TAPI_ACCOUNT_STATE_NORMAL = 'N';
    //! ����
    const TAPIAccountState            TAPI_ACCOUNT_STATE_CANCEL = 'C';
    //! ����
    const TAPIAccountState            TAPI_ACCOUNT_STATE_SLEEP = 'S';
    //! ����(��)
    const TAPIAccountState            TAPI_ACCOUNT_STATE_FROZEN = 'F';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIACCOUNTFAMILYTYPE    �����˻�����
     *    @{
     */
     //=============================================================================
     //! �����˻�����
    typedef TAPICHAR                TAPIAccountFamilyType;
    //! �����˺�
    const    TAPIAccountFamilyType    TAPI_ACCOUNT_FAMILYTYPE_NOMAL = 'N';
    //! ���˻�
    const    TAPIAccountFamilyType    TAPI_ACCOUNT_FAMILYTYPE_CHILD = 'C';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIORDERTYPETYPE    ί������
     *    @{
     */
     //=============================================================================
     //! ί������
    typedef TAPICHAR                TAPIOrderTypeType;
    //! �м�
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_MARKET = '1';
    //! �޼�
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_LIMIT = '2';
    //! �м�ֹ��
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_STOP_MARKET = '3';
    //! �޼�ֹ��
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_STOP_LIMIT = '4';
    //! ��Ȩ��Ȩ
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_OPT_EXEC = '5';
    //! ��Ȩ��Ȩ
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_OPT_ABANDON = '6';
    //! ѯ��
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_REQQUOT = '7';
    //! Ӧ��
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_RSPQUOT = '8';
    //! ����
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_SWAP = '9';
    //! �������
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_COMB = 'A';
    //! �������
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_UNCOMB = 'B';
    //! �м�ֹӯ
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_PROFIT_MARKET = 'C';
    //! �޼�ֹӯ
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_PROFIT_LIMIT = 'D';
    //! �ױ�����
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_HEDGE = 'E';
    //! ��Ȩ�ԶԳ�
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_OPTION_AUTO_CLOSE = 'F';
    //! ��Լ�ڻ��ԶԳ�
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_FUTURE_AUTO_CLOSE = 'G';
    //! ��������������
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_MARKET_POSITION_KEEP = 'H';
    //! ������ȡ���������Զ���Ȩ
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_OPTION_AUTOEXEC_ABAND = 'I';
    //! �н���OTCЭ�̶���
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_OTC = 'K';
    //! ��ɽ��
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_ICEBERG = 'Z';
    //! Ӱ�ӵ�
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_GHOST = 'Y';
    //! �۽������۵�
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_HKEX_AUCTION = 'X';
    //! ֤ȯ����
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_LOCK = 'W';
    //! ֤ȯ����
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_UNLOCK = 'V';
    //! ��ǿ�޼۵�
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_ENHANCE = 'U';
    //! �ر��޼۵�
    const TAPIOrderTypeType            TAPI_ORDER_TYPE_SPECIAL = 'T';
    //! �����޼۵�
    const TAPIOrderTypeType         TAPI_ORDER_TYPE_LIMIT_AUCTION = 'S';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIORDERSOURCETYPE    ί����Դ
     *    @{
     */
     //=============================================================================
     //! ί����Դ
    typedef TAPICHAR                TAPIOrderSourceType;
    //! �������ӵ�
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_SELF_ETRADER = '1';
    //! ������ӵ�
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_PROXY_ETRADER = '2';
    //! �ⲿ���ӵ�(�ⲿ����ϵͳ�µ�����ϵͳ¼��)
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_JTRADER = '3';
    //! �˹�¼�뵥(�ⲿ������ʽ�µ�����ϵͳ¼��)
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_MANUAL = '4';
    //! carry��
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_CARRY = '5';
    //! ��ʽ������
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_PROGRAM = '6';
    //! ������Ȩ
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_DELIVERY = '7';
    //! ��Ȩ����
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_ABANDON = '8';
    //! ͨ����
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_CHANNEL = '9';
    //! ��ʢAPI
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_ESUNNY_API = 'A';
    //! ��ʢV8�ͻ���
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_ESV8CLIENT = 'B';
    //! ��ʢ���ǿͻ���
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_EPOLESTAR = 'F';
    //! ��ʢ���ǿͻ���
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_ESTAR = 'D';
    //! ��������Ȩ��Ȩ��Գ�
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_DCEAFTEREX = 'E';
    //! ��Ȩ��Լ
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_COMPLIANCE = 'C';
    //! ��Ȩ�Գ�
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_OPTIONHEDGE = 'I';
    //! �ڻ��Գ�
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_FUTUREHEDGE = 'J';
    //! ��Ȩ����
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_OPTIONEXCE = 'K';
    //! ��ʢapi UDP��ʽ
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_ESUNNY_API_UDP = 'G';
    //! ��ʢ8.5�ͻ���
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_ESV85CLIENT = 'L';
    //! ��ʢ9.5�ͻ���
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_ESV95CLIENT = 'M';
    //! ��ʢ�Ʋ��Ե�
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_EPOLECLOUD = 'N';
    //! ��ʢ��������
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_ESQUANT = 'O';
    //! Bloomberg�µ�
    const TAPIOrderSourceType        TAPI_ORDER_SOURCE_BLOOMBERG = 'Z';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPITIMEINFORCETYPE    ί����Ч����
     *    @{
     */
     //=============================================================================
     //! ί����Ч����
    typedef TAPICHAR                TAPITimeInForceType;
    //! ������Ч(�ֻ�����ֻ֧�ָ�����)
    const TAPITimeInForceType        TAPI_ORDER_TIMEINFORCE_GFD = '0';
    //! ȡ��ǰ��Ч
    const TAPITimeInForceType        TAPI_ORDER_TIMEINFORCE_GTC = '1';
    //! ָ������ǰ��Ч
    const TAPITimeInForceType        TAPI_ORDER_TIMEINFORCE_GTD = '2';
    //! FAK��IOC
    const TAPITimeInForceType        TAPI_ORDER_TIMEINFORCE_FAK = '3';
    //! FOK
    const TAPITimeInForceType        TAPI_ORDER_TIMEINFORCE_FOK = '4';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPISIDETYPE    ��������
     *    @{
     */
     //=============================================================================
     //! ��������
    typedef TAPICHAR                TAPISideType;
    //! ��
    const TAPISideType                TAPI_SIDE_NONE = 'N';
    //! ����
    const TAPISideType                TAPI_SIDE_BUY = 'B';
    //! ����
    const TAPISideType                TAPI_SIDE_SELL = 'S';
    //! ˫��
    const TAPISideType                TAPI_SIDE_ALL = 'A';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIPOSITIONEFFECTTYPE    ��ƽ����
     *    @{
     */
     //=============================================================================
     //! ��ƽ����
    typedef TAPICHAR                TAPIPositionEffectType;
    //! ���ֿ�ƽ
    const TAPIPositionEffectType    TAPI_PositionEffect_NONE = 'N';
    //! ����
    const TAPIPositionEffectType    TAPI_PositionEffect_OPEN = 'O';
    //! ƽ��
    const TAPIPositionEffectType    TAPI_PositionEffect_COVER = 'C';
    //! ƽ����
    const TAPIPositionEffectType    TAPI_PositionEffect_COVER_TODAY = 'T';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIHEDGEFLAGTYPE    Ͷ����ֵ����
     *    @{
     */
     //=============================================================================
     //! Ͷ����ֵ����
    typedef TAPICHAR                TAPIHedgeFlagType;
    //! ��
    const TAPIHedgeFlagType            TAPI_HEDGEFLAG_NONE = 'N';
    //! Ͷ��
    const TAPIHedgeFlagType            TAPI_HEDGEFLAG_T = 'T';
    //! ��ֵ
    const TAPIHedgeFlagType            TAPI_HEDGEFLAG_B = 'B';
    //! ����
    const TAPIHedgeFlagType            TAPI_HEDGEFLAG_L = 'L';
    //! ������
    const TAPIHedgeFlagType            TAPI_HEDGEFLAG_M = 'M';
    //! ICAƷ��
    const TAPIHedgeFlagType            TAPI_HEDGEFLAG_I = 'I';
    //! CME�Զ���
    const TAPIHedgeFlagType            TAPI_HEDGEFLAG_C = 'C';
    //! ����
    const TAPIHedgeFlagType            TAPI_HEDGEFLAG_R = 'R';
    //! CME�����Գɽ�
    const TAPIHedgeFlagType            TAPI_HEDGEFLAG_S = 'S';
    //! �����ϱ����˺�
    const TAPIHedgeFlagType            TAPI_HEDGEFLAG_F = 'F';
    //! CME�ϱ��µ��˵�ַ
    const TAPIHedgeFlagType            TAPI_HEDGEFLAG_Z = 'Z';

    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIORDERSTATETYPE    ί��״̬����
     *    @{
     */
     //=============================================================================
     //! ί��״̬����
    typedef TAPICHAR                TAPIOrderStateType;
    //! �ն��ύ
    const TAPIOrderStateType        TAPI_ORDER_STATE_SUBMIT = '0';
    //! ������
    const TAPIOrderStateType        TAPI_ORDER_STATE_ACCEPT = '1';
    //! ���Դ�����
    const TAPIOrderStateType        TAPI_ORDER_STATE_TRIGGERING = '2';
    //! ������������
    const TAPIOrderStateType        TAPI_ORDER_STATE_EXCTRIGGERING = '3';
    //! ���Ŷ�
    const TAPIOrderStateType        TAPI_ORDER_STATE_QUEUED = '4';
    //! ���ֳɽ�
    const TAPIOrderStateType        TAPI_ORDER_STATE_PARTFINISHED = '5';
    //! ��ȫ�ɽ�
    const TAPIOrderStateType        TAPI_ORDER_STATE_FINISHED = '6';
    //! ������(�Ŷ���ʱ״̬)
    const TAPIOrderStateType        TAPI_ORDER_STATE_CANCELING = '7';
    //! ���޸�(�Ŷ���ʱ״̬)
    const TAPIOrderStateType        TAPI_ORDER_STATE_MODIFYING = '8';
    //! ��ȫ����
    const TAPIOrderStateType        TAPI_ORDER_STATE_CANCELED = '9';
    //! �ѳ��൥
    const TAPIOrderStateType        TAPI_ORDER_STATE_LEFTCANCELED = 'A';
    //! ָ��ʧ��
    const TAPIOrderStateType        TAPI_ORDER_STATE_FAIL = 'B';
    //! ����ɾ��
    const TAPIOrderStateType        TAPI_ORDER_STATE_DELETED = 'C';
    //! �ѹ���
    const TAPIOrderStateType        TAPI_ORDER_STATE_SUPPENDED = 'D';
    //! ����ɾ��
    const TAPIOrderStateType        TAPI_ORDER_STATE_DELETEDFOREXPIRE = 'E';
    //! ����Ч--ѯ�۳ɹ�
    const TAPIOrderStateType        TAPI_ORDER_STATE_EFFECT = 'F';
    //! ������--��Ȩ����Ȩ������������ɹ�
    const TAPIOrderStateType        TAPI_ORDER_STATE_APPLY = 'G';
    //! ϵͳɾ��
    const TAPIOrderStateType        TAPI_ORDER_STATE_SYSTEMDELETED = 'H';
    //! �����
    const TAPIOrderStateType        TAPI_ORDER_STATE_CHECKING = 'I';
    //! ���г���
    const TAPIOrderStateType        TAPI_ORDER_STATE_CLOSECANCELED = 'J';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPICALCULATEMODETYPE    ���㷽ʽ
     *    @{
     */
     //=============================================================================
     //! ���㷽ʽ
    typedef TAPICHAR                TAPICalculateModeType;
    //! ����+�������0.01���ֶ�����㣬С��0.01���ֱ�������
    const TAPICalculateModeType        TAPI_CALCULATE_MODE_COMBINE = '0';
    //! ����
    const TAPICalculateModeType        TAPI_CALCULATE_MODE_PERCENTAGE = '1';
    //! ����
    const TAPICalculateModeType        TAPI_CALCULATE_MODE_QUOTA = '2';
    //! ��ֵ����
    const TAPICalculateModeType        TAPI_CALCULATE_MODE_CHAPERCENTAGE = '3';
    //! ��ֵ����
    const TAPICalculateModeType        TAPI_CALCULATE_MODE_CHAQUOTA = '4';
    //! �ۿ�
    const TAPICalculateModeType        TAPI_CALCULATE_MODE_DISCOUNT = '5';
    //! ���Է�ʽ
    const TAPICalculateModeType        TAPI_CALCULATE_MODE_ABSOLUTE = '7';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIMATCHSOURCETYPE    �ɽ���Դ
     *    @{
     */
     //=============================================================================
     //! �ɽ���Դ
    typedef TAPICHAR                TAPIMatchSourceType;
    //! ȫ��
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_ALL = '0';
    //! �������ӵ�
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_SELF_ETRADER = '1';
    //! ������ӵ�
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_PROXY_ETRADER = '2';
    //! �ⲿ���ӵ�
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_JTRADER = '3';
    //! �˹�¼�뵥
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_MANUAL = '4';
    //! carry��
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_CARRY = '5';
    //! ��ʽ����
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_PROGRAM = '6';
    //! ������Ȩ
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_DELIVERY = '7';
    //! ��Ȩ����
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_ABANDON = '8';
    //! ͨ����
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_CHANNEL = '9';
    //! ��ʢAPI
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_ESUNNY_API = 'A';
    //! ��ʢV8�ͻ���
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_ESV8CLIENT = 'B';
    //! ��ʢ���ǿͻ���
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_EPOLESTAR = 'F';
    //! ��ʢ���ǿͻ���
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_ESTAR = 'D';
    //! ��������Ȩ��Ȩ��Գ�
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_DCEAFTEREX = 'E';
    //! ��Ȩ��Լ
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_COMPLIANCE = 'C';
    //! ��Ȩ�Գ�
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_OPTIONHEDGE = 'I';
    //! �ڻ��Գ�
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_FUTUREHEDGE = 'J';
    //! ��Ȩ����
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_OPTIONEXCE = 'K';
    //! Bloomberg�µ�
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_BLOOMBERG = 'Z';
    //! GiveUp�ɽ�
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_GIVEUP = 'Y';
    //! ��Ȩ�ɽ�
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_EXERCISE = 'X';
    //! TakeUp�ɽ�
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_TAKEUP = 'W';
    //! ����ת�Ƶĳɽ�ɾ��
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_INPUT_DELETE = '#';
    //! ������
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_ERRORADJUST = 'V';
    //! ���͵��ӵ�
    const TAPIMatchSourceType        TAPI_MATCH_SOURCE_BROKER_ETRADER = 'U';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIOPENCLOSEMODETYPE    ��ƽ��ʽ
     *    @{
     */
     //=============================================================================
     //! ��ƽ��ʽ
    typedef TAPICHAR                TAPIOpenCloseModeType;
    //! �����ֿ�ƽ
    const TAPIOpenCloseModeType        TAPI_CLOSE_MODE_NONE = 'N';
    //! ƽ��δ�˽�
    const TAPIOpenCloseModeType        TAPI_CLOSE_MODE_UNFINISHED = 'U';
    //! ���ֿ��ֺ�ƽ��
    const TAPIOpenCloseModeType        TAPI_CLOSE_MODE_OPENCOVER = 'C';
    //! ���ֿ��֡�ƽ�ֺ�ƽ��
    const TAPIOpenCloseModeType        TAPI_CLOSE_MODE_CLOSETODAY = 'T';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIFUTUREALGTYPE    �ڻ��㷨
     *    @{
     */
     //=============================================================================
     //! �ڻ��㷨
    typedef TAPICHAR                TAPIFutureAlgType;
    //! ���
    const TAPIFutureAlgType            TAPI_FUTURES_ALG_ZHUBI = '1';
    //! ����
    const TAPIFutureAlgType            TAPI_FUTURES_ALG_DINGSHI = '2';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIOPTIONALGTYPE    ��Ȩ�㷨
     *    @{
     */
     //=============================================================================
     //! ��Ȩ�㷨
    typedef TAPICHAR                TAPIOptionAlgType;
    //! �ڻ���ʽ
    const TAPIOptionAlgType         TAPI_OPTION_ALG_FUTURES = '1';
    //! ��Ȩ��ʽ
    const TAPIOptionAlgType         TAPI_OPTION_ALG_OPTION = '2';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIBANKACCOUNTLWFLAGTYPE    ����ұ�ʶ
     *    @{
     */
     //=============================================================================
     //! ����ұ�ʶ
    typedef TAPICHAR                TAPIBankAccountLWFlagType;
    //! ����������˻�
    const TAPIBankAccountLWFlagType    TAPI_LWFlag_L = 'L';
    //! �ͻ���������˻�
    const TAPIBankAccountLWFlagType    TAPI_LWFlag_W = 'W';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIMARGINCALCULATEMODETYPE    �ڻ���֤��ʽ
     *    @{
     */
     //=============================================================================
     //! �ڻ���֤��ʽ
    typedef TAPICHAR                TAPIMarginCalculateModeType;
    //! �ֱ�
    const TAPIMarginCalculateModeType TAPI_DEPOSITCALCULATE_MODE_FEN = '1';
    //! ����
    const TAPIMarginCalculateModeType TAPI_DEPOSITCALCULATE_MODE_SUO = '2';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIOPTIONMARGINCALCULATEMODETYPE    ��Ȩ��֤��ʽ
     *    @{
     */
     //=============================================================================
     //! ��Ȩ��֤��ʽ,�ݴ��жϸ�Ʒ����Ȩ���ú������ü��㹫ʽ���㱣֤��
    typedef TAPICHAR                TAPIOptionMarginCalculateModeType;
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPICMBDIRECTTYPE    ��Ϸ���
     *    @{
     */
     //=============================================================================
     //! ��Ϸ���,Ʒ��������Ϻ�Լ����������͵ڼ�����ͬ
    typedef TAPICHAR                TAPICmbDirectType;
    //! �͵�һ��һ��
    const TAPICmbDirectType         TAPI_CMB_DIRECT_FIRST = '1';
    //! �͵ڶ���һ��
    const TAPICmbDirectType         TAPI_CMB_DIRECT_SECOND = '2';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIDELIVERYMODETYPE    ������Ȩ��ʽ
     *    @{
     */
     //=============================================================================
     //! ������Ȩ��ʽ,�ڻ�����Ȩ�˽�ķ�ʽ
    typedef TAPICHAR                TAPIDeliveryModeType;
    //! ʵ�ｻ��
    const TAPIDeliveryModeType        TAPI_DELIVERY_MODE_GOODS = 'G';
    //! �ֽ𽻸�
    const TAPIDeliveryModeType        TAPI_DELIVERY_MODE_CASH = 'C';
    //! ��Ȩ��Ȩ
    const TAPIDeliveryModeType        TAPI_DELIVERY_MODE_EXECUTE = 'E';
    //! ��Ȩ����
    const TAPIDeliveryModeType        TAPI_DELIVERY_MODE_ABANDON = 'A';
    //! �۽�����Ȩ
    const TAPIDeliveryModeType        TAPI_DELIVERY_MODE_HKF = 'H';
    //! TAS��ʽ
    const TAPIDeliveryModeType        TAPI_DELIVERY_MODE_TAS = 'T';
    //! ��Ȩ�Գ�
    const TAPIDeliveryModeType        TAPI_DELIVERY_MODE_OPTIONHEDGE = 'I';
    //! �ڻ��Գ�
    const TAPIDeliveryModeType        TAPI_DELIVERY_MODE_FUTUREHEDGE = 'J';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPICONTRACTTYPETYPE    ��Լ����
     *    @{
     */
     //=============================================================================
     //! ��Լ����
    typedef TAPICHAR                TAPIContractTypeType;
    //! ���������Լ
    const TAPIContractTypeType        TAPI_CONTRACT_TYPE_TRADEQUOTE = '1';
    //! �����Լ
    const TAPIContractTypeType        TAPI_CONTRACT_TYPE_QUOTE = '2';
    /** @}*/

    //=============================================================================
    //T+1�ɽ�
    typedef TAPICHAR                TAPIIsAddOneType;
    //T+1�ɽ�
    const TAPIIsAddOneType            TAPI_ISADD_ONE_YES = 'Y';
    //��T+1�ɽ�
    const TAPIIsAddOneType            TAPI_ISADD_ONE_NO = 'N';

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPITACTICSTYPETYPE    ���Ե�����
     *    @{
     */
     //=============================================================================
     //! ���Ե�����
    typedef TAPICHAR                TAPITacticsTypeType;
    //! ��
    const TAPITacticsTypeType        TAPI_TACTICS_TYPE_NONE = 'N';
    //! Ԥ����(��)
    const TAPITacticsTypeType        TAPI_TACTICS_TYPE_READY = 'M';
    //! �Զ���
    const TAPITacticsTypeType        TAPI_TACTICS_TYPE_ATUO = 'A';
    //! ������
    const TAPITacticsTypeType        TAPI_TACTICS_TYPE_CONDITION = 'C';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIORDERACT    ������������
     *    @{
     */
     //=============================================================================
     //! ������������
    typedef TAPICHAR                TAPIORDERACT;
    //! ����
    const TAPIORDERACT                APIORDER_INSERT = '1';
    //! �ĵ�
    const TAPIORDERACT                APIORDER_MODIFY = '2';
    //! ����
    const TAPIORDERACT                APIORDER_DELETE = '3';
    //! ����
    const TAPIORDERACT                APIORDER_SUSPEND = '4';
    //! ����
    const TAPIORDERACT                APIORDER_ACTIVATE = '5';
    //! ɾ��
    const TAPIORDERACT                APIORDER_SYSTEM_DELETE = '6';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPITRIGGERCONDITIONTYPE    ������������
     *    @{
     */
     //=============================================================================
     //! ������������
    typedef TAPICHAR                TAPITriggerConditionType;
    //! ��
    const TAPITriggerConditionType    TAPI_TRIGGER_CONDITION_NONE = 'N';
    //! ���ڵ���
    const TAPITriggerConditionType    TAPI_TRIGGER_CONDITION_GREAT = 'G';
    //! С�ڵ���
    const TAPITriggerConditionType    TAPI_TRIGGER_CONDITION_LITTLE = 'L';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPITRIGGERPRICETYPETYPE    �����۸�����
     *    @{
     */
     //=============================================================================
     //! �����۸�����
    typedef TAPICHAR                TAPITriggerPriceTypeType;
    //! ��
    const TAPITriggerPriceTypeType    TAPI_TRIGGER_PRICE_NONE = 'N';
    //! ���
    const TAPITriggerPriceTypeType    TAPI_TRIGGER_PRICE_BUY = 'B';
    //! ����
    const TAPITriggerPriceTypeType    TAPI_TRIGGER_PRICE_SELL = 'S';
    //! ���¼�
    const TAPITriggerPriceTypeType    TAPI_TRIGGER_PRICE_LAST = 'L';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIMARKETLEVELTYPE    �м۴�����
     *    @{
     */
     //=============================================================================
     //! �м۴�����
    typedef TAPIUINT8                TAPIMarketLevelType;
    //! �����
    const TAPIMarketLevelType        TAPI_MARKET_LEVEL_0 = 0;
    //! 1�����ż�
    const TAPIMarketLevelType        TAPI_MARKET_LEVEL_1 = 1;
    //! 5��
    const TAPIMarketLevelType        TAPI_MARKET_LEVEL_5 = 5;
    //! 10��
    const TAPIMarketLevelType        TAPI_MARKET_LEVEL_10 = 10;
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPITRADINGSTATETYPE    ����״̬
     *    @{
     */
     //=============================================================================
     //! ����״̬
    typedef TAPICHAR                TAPITradingStateType;
    //! ���Ͼ���
    const TAPITradingStateType        TAPI_TRADE_STATE_BID = '1';
    //! ���Ͼ��۴��
    const TAPITradingStateType        TAPI_TRADE_STATE_MATCH = '2';
    //! ��������
    const TAPITradingStateType        TAPI_TRADE_STATE_CONTINUOUS = '3';
    //! ������ͣ
    const TAPITradingStateType        TAPI_TRADE_STATE_PAUSED = '4';
    //! ����
    const TAPITradingStateType        TAPI_TRADE_STATE_CLOSE = '5';
    //! ���д���ʱ��
    const TAPITradingStateType        TAPI_TRADE_STATE_DEALLAST = '6';
    //! ����δ��
    const TAPITradingStateType        TAPI_TRADE_STATE_GWDISCONNECT = '0';
    //! δ֪״̬
    const TAPITradingStateType        TAPI_TRADE_STATE_UNKNOWN = 'N';
    //! ����ʼ��
    const TAPITradingStateType        TAPI_TRADE_STATE_INITIALIZE = 'I';
    //! ׼������
    const TAPITradingStateType        TAPI_TRADE_STATE_READY = 'R';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPINOTICEIGNOREFLAGTYPE    ���Ժ�̨����֪ͨ���
     *    @{
     */
     //=============================================================================
     //! ���Ժ�̨����֪ͨ���
    typedef TAPIUINT32                TAPINoticeIgnoreFlagType;
    //! ����������Ϣ
    const TAPINoticeIgnoreFlagType    TAPI_NOTICE_IGNORE_NONE = 0x00000000;
    //! ������������
    const TAPINoticeIgnoreFlagType    TAPI_NOTICE_IGNORE_ALL = 0xFFFFFFFF;
    //! �����ʽ�����:OnRtnFund
    const TAPINoticeIgnoreFlagType    TAPI_NOTICE_IGNORE_FUND = 0x00000001;
    //! ����ί������:OnRtnOrder
    const TAPINoticeIgnoreFlagType    TAPI_NOTICE_IGNORE_ORDER = 0x00000002;
    //! ���Գɽ�����:OnRtnFill
    const TAPINoticeIgnoreFlagType    TAPI_NOTICE_IGNORE_FILL = 0x00000004;
    //! ���Գֲ�����:OnRtnPosition
    const TAPINoticeIgnoreFlagType    TAPI_NOTICE_IGNORE_POSITION = 0x00000008;
    //! ����ƽ������:OnRtnClose
    const TAPINoticeIgnoreFlagType    TAPI_NOTICE_IGNORE_CLOSE = 0x00000010;
    //! ���Գֲ�ӯ������:OnRtnPositionProfit
    const TAPINoticeIgnoreFlagType    TAPI_NOTICE_IGNORE_POSITIONPROFIT = 0x00000020;
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIORDERQRYTYPETYPE    ί�в�ѯ����
     *    @{
     */
     //=============================================================================
     //! ί�в�ѯ����
    typedef TAPICHAR                TAPIOrderQryTypeType;
    //! ��������ί��
    const TAPIOrderQryTypeType        TAPI_ORDER_QRY_TYPE_ALL = 'A';
    //! ֻ����δ������ί��
    const TAPIOrderQryTypeType        TAPI_ORDER_QRY_TYPE_UNENDED = 'U';
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPISystemTypeTypeE    ��̨ϵͳ����
     *    @{
     */
     //=============================================================================
     //! ��̨ϵͳ����
    typedef TAPIUINT32                TAPISystemTypeType;
    //! ����������ϵͳ
    const TAPISystemTypeType        TAPI_SYSTEM_TYPE_ESUNNY = 1;
    //! ���̱�����ϵͳ
    const TAPISystemTypeType        TAPI_SYSTEM_TYPE_IESUNNY = 2;
    //! �ֻ���̨ϵͳ
    const TAPISystemTypeType        TAPI_SYSTEM_TYPE_CELLPHONE = 3;
    //! ETF������ϵͳ
    const TAPISystemTypeType        TAPI_SYSTEM_TYPE_ETF = 4;
    //! ��Ʊϵͳ
    const TAPISystemTypeType        TAPI_SYSTEM_TYPE_STOCK = 5;
    /** @}*/

    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_LOGINTPYE    ��¼����
     *    @{
     */
     //=============================================================================
     //! ��¼����
    typedef TAPIUINT32                TAPILoginTypeType;
    //! ��ͨTCP
    const TAPILoginTypeType            TAPI_LOGINTYPE_NORMAL = 1;
    //! ����TCP(�ݲ�֧��)
    const TAPILoginTypeType            TAPI_LOGINTYPE_GMSSL = 2;
    //! OpenSSL(������ר��)
    const TAPILoginTypeType            TAPI_LOGINTYPE_OPENSSL = 3;
    /** @}*/

    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_T_TAPIMSGLEVELTYPE    ��Ϣ����
    *    @{
    */
    //=============================================================================
    //! ��Ϣ����
    typedef TAPICHAR                TAPIMsgLevelType;
    //! ��ͨ
    const TAPIMsgLevelType            TAPI_MSG_LEVEL_NORMAL = '1';
    //! ��Ҫ
    const TAPIMsgLevelType            TAPI_MSG_LEVEL_IMPORTANT = '2';
    //! ����
    const TAPIMsgLevelType            TAPI_MSG_LEVEL_IMERGENCY = '3';
    /** @}*/

    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_T_TAPIMSGTYPETYPE    ��Ϣ����
    *    @{
    */
    //=============================================================================
    //! ��Ϣ����
    typedef TAPICHAR                TAPIMsgTypeType;
    //! ����
    const TAPIMsgTypeType            TAPI_Msg_TYPE_MANAGER = '1';
    //! ����
    const TAPIMsgTypeType            TAPI_Msg_TYPE_RISKCONTROL = '2';
    /** @}*/

    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_T_TAPIMSGQRYTYPETYPE    ��Ϣ���Ͳ�ѯ����
    *    @{
    */
    //=============================================================================
    //! ��Ϣ��ѯ����(������ר�ã������Ǻ�̨Ĭ��ȫ��)
    typedef TAPICHAR                TAPIMsgQryTypeType;
    //! ȫ��
    const TAPIMsgQryTypeType        TAPI_Msg_QRYTYPE_ALL = 'A';
    //! ��Ч
    const TAPIMsgQryTypeType        TAPI_Msg_QRYTYPE_VALID = 'Y';
    /** @}*/

    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_T_TAPICASHADJUSTTYPETYPE    �ʽ��������
    *    @{
    */
    //=============================================================================
    //! �ʽ��������
    typedef TAPICHAR                        TAPICashAdjustTypeType;
    //! �����ѵ���
    const TAPICashAdjustTypeType            TAPI_CASHINOUT_MODE_FEEADJUST = '0';
    //! ӯ������
    const TAPICashAdjustTypeType            TAPI_CASHINOUT_MODE_YKADJUST = '1';
    //! ��Ѻ�ʽ�
    const TAPICashAdjustTypeType            TAPI_CASHINOUT_MODE_PLEDGE = '2';
    //! ��Ϣ����
    const TAPICashAdjustTypeType            TAPI_CASHINOUT_MODE_INTERESTREVENUE = '3';
    //! ���۷���
    const TAPICashAdjustTypeType            TAPI_CASHINOUT_MODE_COLLECTIONCOST = '4';
    //! ����
    const TAPICashAdjustTypeType            TAPI_CASHINOUT_MODE_OTHER = '5';
    //! ��˾�䲦��
    const TAPICashAdjustTypeType            TAPI_CASHINOUT_MODE_COMPANY = '6';
    //! �Զ�ת��
    const TAPICashAdjustTypeType            TAPI_CASHINOUT_MODE_AUTOADJUST = '7';
    //! ��Ʊ�ڻ�����
    const TAPICashAdjustTypeType            TAPI_CASHINOUT_MODE_STOCKADJSUT = '8';
    /** @}*/

    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_T_TAPIBILLTYPETYPE    �˵�����
    *    @{
    */
    //=============================================================================
    //! �˵�����
    typedef TAPICHAR                TAPIBillTypeType;
    //! ���˵�
    const TAPIBillTypeType            TAPI_BILL_DATE = 'D';
    //! ���˵�
    const TAPIBillTypeType            TAPI_BILL_MONTH = 'M';
    /** @}*/

    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_T_TAPIBILLFILETYPETYPE    �ʵ��ļ�����
    *    @{
    */
    //=============================================================================
    //! �ʵ��ļ�����
    typedef TAPICHAR                TAPIBillFileTypeType;
    //! txt��ʽ�ļ�
    const TAPIBillFileTypeType        TAPI_BILL_FILE_TXT = 'T';
    //! pdf��ʽ�ļ�
    const TAPIBillFileTypeType        TAPI_BILL_FILE_PDF = 'F';
    /** @}*/

    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_T_TAPIAUTHTYPETYPE    ��Ȩ��¼�ļ�����
    *    @{
    */
    //=============================================================================
    //! ��Ȩ��¼�ļ�����
    typedef TAPICHAR                TAPIAuthTypeType;
    //! ֱ��ģʽ
    const TAPIAuthTypeType            TAPI_AUTHTYPE_DIRECT = '1';
    //! �м�ģʽ
    const TAPIAuthTypeType            TAPI_AUTHTYPE_RELAY = '2';
    /** @}*/

    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_T_TAPISENDTYPETYPE    ������֤���ͷ�ʽ
    *    @{
    */
    //=============================================================================
    //! ������֤���ͷ�ʽ
    typedef TAPICHAR                TAPISendTypeType;
    //! ����
    const TAPISendTypeType          TAPI_SENDTYPE_SMS = 'S';
    //! �ʼ�
    const TAPISendTypeType          TAPI_SENDTYPE_MAIL = 'M';
    //! ΢��
    const TAPISendTypeType          TAPI_SENDTYPE_WEIXIN = 'W';
    /** @}*/

    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_T_TAPISECONDLOGINTYPETYPE  ������֤��¼����
    *    @{
    */
    //=============================================================================
    //! ������֤��¼����
    typedef TAPICHAR                TAPISecondLoginTypeType;
    //! ������¼�������豸��
    const TAPISecondLoginTypeType        TAPI_ILOGINTYPE_NORMAL = 'N';
    //! ��ʱ��¼
    const TAPISecondLoginTypeType        TAPI_ILOGINTYPE_TEMPORARY = 'T';
    //! ������������
    const TAPISecondLoginTypeType        TAPI_LOGINTYPE_RESETPASSWORD = 'R';
    //! ����״̬�ⶳ
    const TAPISecondLoginTypeType        TAPI_LOGINTYPE_UNFREEZE = 'U';
    /** @}*/

    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_T_TAPIDEVICETYPETYPE    �ֻ��豸����
    *    @{
    */
    //=============================================================================
    //! �ֻ��豸����
    typedef TAPICHAR                TAPIDeviceTypeType;
    //! Android
    const TAPIDeviceTypeType        TAPI_DEVICETYPE_ANDROID = '0';
    //! IOS
    const TAPIDeviceTypeType        TAPI_DEVICETYPE_IOS = '1';
    /** @}*/

    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_T_TAPISPECIALORDERTYPETYPE    ����ҵ��ί������
    *    @{
    */
    //=============================================================================
    //! ����ҵ��ί������
    typedef TAPICHAR                    TAPISpecialOrderTypeType;
    //! ��ϲ�������
    const TAPISpecialOrderTypeType      TAPI_STRATEGY_COMBINE = '1';
    //! ��ϲ��Բ��
    const TAPISpecialOrderTypeType      TAPI_STRATEGY_SPLIT = '2';
    //! ֤ȯ����
    const TAPISpecialOrderTypeType      TAPI_SPOT_LOCK = '3';
    //! ֤ȯ����
    const TAPISpecialOrderTypeType      TAPI_SPOT_UNLOCK = '4';
    //! ��Ȩ��Ȩ
    const TAPISpecialOrderTypeType      TAPI_OPTION_EXERCISE = '5';
    //! ��Ȩ�����Ȩ
    const TAPISpecialOrderTypeType      TAPI_OPTION_EXERCISE_COMBINE = '6';
    /** @}*/

    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_T_TAPICOMBINESTRATEGYTYPE    ��ϲ��Դ���
    *    @{
    */
    //=============================================================================
    //! ��ϲ��Դ���
    typedef TAPICHAR                    TAPICombineStrategyType[11];
    //! �Ϲ�ţ�м۲����
    const TAPICombineStrategyType       TAPI_STRATEGY_C_BULL = "CNSJC";
    //! �Ϲ����м۲����
    const TAPICombineStrategyType       TAPI_STRATEGY_P_BEAR = "PXSJC";
    //! �Ϲ�ţ�м۲����
    const TAPICombineStrategyType       TAPI_STRATEGY_P_BULL = "PNSJC";
    //! �Ϲ����м۲����
    const TAPICombineStrategyType       TAPI_STRATEGY_C_BEAR = "CXSJC";
    //! ��ʽ��ͷ����
    const TAPICombineStrategyType       TAPI_STRATEGY_S_STRADDLE = "KS";
    //! ���ʽ��ͷ����
    const TAPICombineStrategyType       TAPI_STRATEGY_S_STRANGLE = "KKS";
    //! ��ͨ��ת���Ҳ�
    const TAPICombineStrategyType       TAPI_STRATEGY_ZBD = "ZBD";
    //! ���Ҳ�ת��ͨ��
    const TAPICombineStrategyType       TAPI_STRATEGY_ZXJ = "ZXJ";
    /** @}*/

    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_SETTLEFLAG    ��������
    *    @{
    */
    //=============================================================================
    //! ��������
    typedef TAPICHAR                        TAPISettleFlagType;
    //! �Զ�����
    const TAPISettleFlagType                TAPI_SettleFlag_AutoSettle = '0';
    //! �˹�����
    const TAPISettleFlagType                TAPI_SettleFlagh_Manual = '2';
    /** @}*/
    
    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_FORCEMODIFYPASSWORD    �Ƿ�ǿ���޸���������
    *    @{
    */
    //=============================================================================
    //! �Ƿ�ǿ���޸���������
    typedef TAPICHAR                        TAPIForceModifyPasswordType;
    //! ��Ҫǿ���޸�����
    const TAPIForceModifyPasswordType       TAPI_ForceModifyPassword_Yes = 'Y';
    //! ����Ҫǿ���޸�����
    const TAPIForceModifyPasswordType       TAPI_ForceModifyPassword_No = 'N';
    //! ��������(������ר��)
    const TAPIForceModifyPasswordType       TAPI_ForceModifyPassword_Reset = 'R';
    //! �����ⶳ(������ר��)
    const TAPIForceModifyPasswordType       TAPI_ForceModifyPassword_SELFUNFREEZE = 'U';
    /** @}*/
    
    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_CERTIFICATE    ֤������
    *    @{
    */
    //=============================================================================
    //! ֤������
    typedef TAPICHAR                        TAPICertificateType;
    //! ֤������1���ڵ����֤
    const TAPICertificateType               TAPI_CERTIFICATE_TYPE_ONE = '1';
    //! ֤������6���й�����/�ڵظ۰�ͨ��֤
    const TAPICertificateType               TAPI_CERTIFICATE_TYPE_SIX = '6';
    //! ֤������9��Ӫҵִ��
    const TAPICertificateType               TAPI_CERTIFICATE_TYPE_NINE = '9';
    //! ֤������B���������֤
    const TAPICertificateType               TAPI_CERTIFICATE_TYPE_B = 'B';
    //! ֤������X����ҵ�Ǽ�֤
    const TAPICertificateType               TAPI_CERTIFICATE_TYPE_R = 'R';
    /** @}*/
    
    //=============================================================================
    /**
    *    \addtogroup G_DATATYPE_PASSWORD    ��������
    *    @{
    */
    //=============================================================================
    //! ��������
    typedef TAPICHAR                        TAPIPasswordType;
    //! �����������ʹ���, ������֤ʹ��
    const TAPIPasswordType                  TAPI_PASSWORD_TYPE_TRADE = 'T';
    //! ��������(����ר��)
    const TAPIPasswordType                  TAPI_PASSWORD_TYPE_RESET = 'R';
    //! �����ⶳ(����ר��)
    const TAPIPasswordType                  TAPI_PASSWORD_TYPE_UNFREEZE = 'U';
    /** @}*/
    
    //=============================================================================
    /**
     *    \addtogroup G_DATATYPE_T_TAPIOPERATINGSYSTEMTYPE    ����ϵͳ����
     *    @{
     */
    //=============================================================================
    //! ����ϵͳ����
    typedef TAPICHAR                        TAPIOperatingSystemType;
    //! windows
    const TAPIOperatingSystemType           TAPI_OPERATINGSYS_WINDOWS = '1';
    //! linux
    const TAPIOperatingSystemType           TAPI_OPERATINGSYS_LINUX = '2';
    //! MAC-IOS
    const TAPIOperatingSystemType           TAPI_PERATINGSYS_MAC_IOS = '3';
    //! PHONE-IOS
    const TAPIOperatingSystemType           TAPI_OPERATINGSYS_PHONE_IOS = '4';
    //! Android
    const TAPIOperatingSystemType           TAPI_OPERATINGSYS_ANDROID = '5';
    /** @}*/

#pragma pack(pop)
}
#endif
