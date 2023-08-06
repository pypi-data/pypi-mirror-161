//=============================================================================
/* ����ʢͳһ����API�ӿ�
 * ���ļ�������EsTradeAPI ʹ�õ����ݽṹ
 * �汾��Ϣ:2018-05-21 ������ �������ļ�
 */
//=============================================================================
#ifndef ES_TRADE_API_STRUCT_H
#define ES_TRADE_API_STRUCT_H

#include "EsTradeAPIDataType.h"

namespace EsTradeAPI
{

#pragma pack(push, 1)

//------------------------------------------------------------------------------------------
//! ��¼�û���Ϣ
struct TapAPITradeUserInfo
{
    TAPISystemTypeType            SystemType;                            ///< ��̨ϵͳ����
    TAPISTR_20                    UserNo;                                ///< �û����
    TAPISTR_40                    LoginIP;                            ///< ��¼IP
    TAPIUINT32                    LoginPort;                            ///< ��¼�˿�
    TAPILoginTypeType            LoginType;                            ///< ��¼����
};

//! ��¼��֤��Ϣ
struct TapAPITradeLoginAuth
{
    TAPISTR_20                    UserNo;                                ///< �û���
    TAPIUserTypeType            UserType;                            ///< �û�����
    TAPISTR_50                    AuthCode;                            ///< ��Ȩ��
    TAPISTR_30                    AppID;                                ///< Ӧ�ó����
    TAPIForceModifyPasswordType    ISModifyPassword;                    ///< �Ƿ��޸�����
    TAPISTR_20                    Password;                            ///< ����
    TAPISTR_20                    NewPassword;                        ///< ������
    TAPIYNFLAG                    ISDDA;                                ///< �Ƿ���Ҫ��̬��֤
    TAPISTR_30                    DDASerialNo;                        ///< ��̬��֤��
    TAPINoticeIgnoreFlagType    NoticeIgnoreFlag;                    ///< ��������֪ͨ���
    TAPISTR_40                  LoginIP;                            ///< ��¼�û�IP
    TAPISTR_50                  LoginMac;                           ///< ��¼�û�MAC
};

//! ��¼������Ϣ
struct TapAPITradeLoginRspInfo
{
    TAPISTR_20                    UserNo;                                ///< �û����
    TAPIUserTypeType            UserType;                            ///< �û�����
    TAPISTR_20                    UserName;                            ///< �û���
    TAPISTR_20                    QuoteTempPassword;                    ///< ������ʱ����
    TAPISTR_50                    ReservedInfo;                        ///< Ԥ����Ϣ
    TAPISTR_40                    LastLoginIP;                        ///< �ϴε�¼IP
    TAPIUINT32                    LastLoginPort;                        ///< �ϴε�¼�˿�
    TAPIDATETIME                LastLoginTime;                        ///< �ϴε�¼ʱ��
    TAPIDATETIME                LastLogoutTime;                        ///< �ϴ��˳�ʱ��
    TAPIDATE                    TradeDate;                            ///< ��ǰ��������
    TAPIDATETIME                LastSettleTime;                        ///< �ϴν���ʱ��
    TAPIDATETIME                StartTime;                            ///< ϵͳ����ʱ��
    TAPIDATETIME                InitTime;                            ///< ϵͳ��ʼ��ʱ��
    TAPIAuthTypeType            AuthType;                            ///< �û���Ȩ����
    TAPIDATETIME                AuthDate;                            ///< �û���Ȩ������
    TAPIUINT64                    UdpCertCode;                        ///< UDP������֤��
    TAPISTR_40                    CurrentLoginIP;                        ///< ��ǰ��¼������IP
    TAPIUINT32                    CurrentLoginPort;                    ///< ��ǰ��¼�������˿�
};

//! �ϱ��û���¼�ɼ���Ϣ
struct TapAPISubmitUserLoginInfo
{
    TAPISTR_20                    UserNo;                                ///< ��¼�û���
    TAPISTR_500                    GatherInfo;                            ///< �û��ն���Ϣ
    TAPISTR_40                    ClientLoginIP;                        ///< �û�����IP
    TAPIUINT32                    ClientLoginPort;                    ///< �û�����Port
    TAPIDATETIME                ClientLoginDateTime;                ///< �û���¼ʱ��
    TAPISTR_30                    ClientAppID;                        ///< �û�AppID
    TAPIUINT32                    AuthKeyVersion;                        ///< �û��ն���Ϣ������Կ�汾��
    TAPISTR_50                  ItemFalg;                           ///< ��Ϣ�ɼ���ɼ������ʶ
    TAPISTR_30                    GatherLibVersion;                    ///< �ɼ���汾��Ϣ
    TAPIYNFLAG                  IsTestKey;                            ///< �Ƿ������Կ
    TAPIOperatingSystemType     OperatingSystmeType;                ///< ����ϵͳ����
};

//! �ϱ��û���¼�ɼ���ϢӦ��
struct TapAPISubmitUserLoginInfoRsp
{
    TAPISTR_20                    UserNo;                                ///< ��¼�û���
    TAPIUINT32                    ErrorCode;                            ///< ������Ϣ��
    TAPISTR_50                    ErrorText;                            ///< ������Ϣ
};

//! ��������Ϣ
struct TapAPIExchangeInfo
{
    TAPISTR_10                    ExchangeNo;                            ///< ����������
    TAPISTR_20                    ExchangeName;                        ///< ����������
};

//! Ʒ�ֱ���ṹ
struct TapAPICommodity
{
    TAPISTR_10                    ExchangeNo;                            ///< ����������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ��
};

//! ����Ʒ����Ϣ
struct TapAPICommodityInfo
{
    TAPISTR_10                    ExchangeNo;                            ///< ����������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ��
    TAPISTR_20                    CommodityName;                        ///< Ʒ������
    TAPISTR_30                    CommodityEngName;                    ///< Ʒ��Ӣ������
    TAPISTR_10                    RelateExchangeNo;                    ///< ����Ʒ�ֽ���������
    TAPICommodityType            RelateCommodityType;                ///< ����Ʒ��Ʒ������
    TAPISTR_10                    RelateCommodityNo;                    ///< ����Ʒ��Ʒ�ֱ��
    TAPISTR_10                    RelateExchangeNo2;                    ///< ����Ʒ��2����������
    TAPICommodityType            RelateCommodityType2;                ///< ����Ʒ��2Ʒ������
    TAPISTR_10                    RelateCommodityNo2;                    ///< ����Ʒ��2Ʒ�ֱ��
    TAPISTR_10                    TradeCurrency;                        ///< ���ױ���
    TAPIREAL64                    ContractSize;                        ///< ÿ�ֳ���
    TAPIOpenCloseModeType        OpenCloseMode;                        ///< ��ƽ��ʽ
    TAPIREAL64                    StrikePriceTimes;                    ///< ִ�м۸���
    TAPIREAL64                    CommodityTickSize;                    ///< ��С�䶯��λ
    TAPIINT32                    CommodityDenominator;                ///< ���۷�ĸ
    TAPICmbDirectType            CmbDirect;                            ///< ��Ϸ���
    TAPIINT32                    OnlyCanCloseDays;                    ///< ֻ��ƽ����ǰ����
    TAPIDeliveryModeType        DeliveryMode;                        ///< ������Ȩ��ʽ
    TAPIINT32                    DeliveryDays;                        ///< ������ƫ��
    TAPITIME                    AddOneTime;                            ///< T+1�ָ�ʱ��
    TAPIINT32                    CommodityTimeZone;                    ///< Ʒ��ʱ��
    TAPIIsAddOneType            IsAddOne;                            ///< �Ƿ���T+1ʱ��
};

//! ��Լ����ṹ
struct TapAPIContract
{
    TapAPICommodity                Commodity;                            ///< Ʒ��
    TAPISTR_10                    ContractNo1;                        ///< ��Լ����1
    TAPISTR_10                    StrikePrice1;                        ///< ִ�м�1
    TAPICallOrPutFlagType        CallOrPutFlag1;                        ///< ���ǿ�����ʾ1
    TAPISTR_10                    ContractNo2;                        ///< ��Լ����2
    TAPISTR_10                    StrikePrice2;                        ///< ִ�м�2
    TAPICallOrPutFlagType        CallOrPutFlag2;                        ///< ���ǿ�����ʾ2
};

//! ���׺�Լ��Ϣ
struct TapAPITradeContractInfo
{
    TAPISTR_10                    ExchangeNo;                            ///< ����������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ��
    TAPISTR_10                    ContractNo1;                        ///< ��Լ����1
    TAPISTR_10                    StrikePrice1;                        ///< ִ�м�1
    TAPICallOrPutFlagType        CallOrPutFlag1;                        ///< ���ǿ�����ʾ1
    TAPISTR_10                    ContractNo2;                        ///< ��Լ����2
    TAPISTR_10                    StrikePrice2;                        ///< ִ�м�2
    TAPICallOrPutFlagType        CallOrPutFlag2;                        ///< ���ǿ�����ʾ2
    //TAPISTR_70                ContractName;                        ///< ��Լ����
    TAPIDATE                    ContractExpDate;                    ///< ��Լ������
    TAPIDATE                    LastTradeDate;                        ///< �������
    TAPIDATE                    FirstNoticeDate;                    ///< �״�֪ͨ��
    //TAPISTR_10                FutureContractNo;                    ///< �ڻ���Լ���(��Ȩ���)
};

//! �޸���������
struct TapAPIChangePasswordReq
{
    TAPIPasswordType            PasswordType;                       ///< ��������
    TAPISTR_20                    OldPassword;                        ///< ������
    TAPISTR_20                    NewPassword;                        ///< ������
};

//! �޸�����Ӧ��
typedef TapAPIChangePasswordReq TapAPIChangePasswordRsp;

//! �û�Ȩ����Ϣ
struct TapAPIUserRightInfo
{
    TAPISTR_20                    UserNo;                                ///< �û����
    TAPIRightIDType                RightID;                            ///< Ȩ��ID
};

//! �û��µ�Ƶ����Ϣ
struct TapAPIUserOrderFrequency
{
    TAPISTR_20                    UserNo;                                ///< �û����
    TAPIUINT32                    UserOrderFrequency;                    ///< �û���������Ƶ��
};

//! �˺������Ϣ��ѯ����
struct TapAPIAccQryReq
{
    TAPISTR_20                    AccountNo;                            ///< �ʽ��˺�
};

//! �ʽ��˺���Ϣ
struct TapAPIAccountInfo
{
    TAPISTR_20                    AccountNo;                            ///< �ʽ��˺�
    TAPIAccountType                AccountType;                        ///< �˺�����
    TAPIAccountState            AccountState;                        ///< �˺�״̬
    TAPISTR_20                    AccountShortName;                    ///< �˺ż��
    //TAPIYNFLAG                AccountIsDocHolder;                    ///< �Ƿ��֤��
    TAPIYNFLAG                    IsMarketMaker;                        ///< �Ƿ���������
    //TAPIAccountFamilyType        AccountFamilyType;                    ///< �����˺�����
};

//! �ͻ��µ�����ṹ
struct TapAPINewOrder
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��ʺ�

    TAPISTR_10                    ExchangeNo;                            ///< ���������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ�������
    TAPISTR_10                    ContractNo;                            ///< ��Լ1
    TAPISTR_10                    StrikePrice;                        ///< ִ�м۸�1
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ſ���1
    TAPISTR_10                    ContractNo2;                        ///< ��Լ2
    TAPISTR_10                    StrikePrice2;                        ///< ִ�м۸�2
    TAPICallOrPutFlagType        CallOrPutFlag2;                        ///< ���ſ���2

    TAPIOrderTypeType            OrderType;                            ///< ί������
    TAPIOrderSourceType            OrderSource;                        ///< ί����Դ
    TAPITimeInForceType            TimeInForce;                        ///< ί����Ч����
    TAPIDATETIME                ExpireTime;                            ///< ��Ч����(GTD�����ʹ��)
    TAPIYNFLAG                    IsRiskOrder;                        ///< �Ƿ���ձ���

    TAPISideType                OrderSide;                            ///< ��������
    TAPIPositionEffectType        PositionEffect;                        ///< ��ƽ��־1
    TAPIPositionEffectType        PositionEffect2;                    ///< ��ƽ��־2
    TAPISTR_50                    InquiryNo;                            ///< ѯ�ۺ�
    TAPIHedgeFlagType            HedgeFlag;                            ///< Ͷ����ֵ1
    TAPIHedgeFlagType            HedgeFlag2;                            ///< Ͷ����ֵ2
    TAPIREAL64                    OrderPrice;                            ///< ί�м۸�1
    TAPIREAL64                    OrderPrice2;                        ///< ί�м۸�2
    TAPIUINT32                    OrderQty;                            ///< ί������1
    TAPIUINT32                    OrderQty2;                            ///< ί������2
    TAPIUINT32                    OrderMinQty;                        ///< ��С�ɽ���
    TAPIUINT32                    MinClipSize;                        ///< ��ɽ����С�����
    TAPIUINT32                    MaxClipSize;                        ///< ��ɽ����������

    TAPIINT32                    RefInt;                                ///< ���Ͳο�ֵ
    TAPIREAL64                    RefDouble;                            ///< ����ο�ֵ(������)
    TAPISTR_50                    RefString;                            ///< �ַ����ο�ֵ

    TAPITacticsTypeType            TacticsType;                        ///< ���Ե�����
    TAPITriggerConditionType    TriggerCondition;                    ///< ��������
    TAPITriggerPriceTypeType    TriggerPriceType;                    ///< �����۸�����
    TAPIREAL64                    StopPrice;                            ///< �����۸�
    TAPIYNFLAG                    AddOneIsValid;                        ///< �Ƿ�T+1��Ч
    TAPIMarketLevelType            MarketLevel;                        ///< �м۴�����
    TAPIYNFLAG                    FutureAutoCloseFlag;                ///< ��Ȩ���ڻ��Ƿ��ԶԳ�
    TAPISTR_10                    UpperChannelNo;                        ///< ����ͨ����

    TAPIClientIDType            ClientID;                            ///< �ͻ����˺ţ�����������˺ţ��������ϱ����˺�(�����Ǻ�̨��))

    TapAPINewOrder()
    {
        memset(this, 0, sizeof(TapAPINewOrder));
        CallOrPutFlag = TAPI_CALLPUT_FLAG_NONE;
        CallOrPutFlag2 = TAPI_CALLPUT_FLAG_NONE;
        OrderSource = TAPI_ORDER_SOURCE_ESUNNY_API;
        TimeInForce = TAPI_ORDER_TIMEINFORCE_GFD;
        PositionEffect = TAPI_PositionEffect_NONE;
        PositionEffect2 = TAPI_PositionEffect_NONE;
        HedgeFlag = TAPI_HEDGEFLAG_NONE;
        HedgeFlag2 = TAPI_HEDGEFLAG_NONE;
        TacticsType = TAPI_TACTICS_TYPE_NONE;
        TriggerCondition = TAPI_TRIGGER_CONDITION_NONE;
        TriggerPriceType = TAPI_TRIGGER_PRICE_NONE;
        AddOneIsValid = APIYNFLAG_NO;
        FutureAutoCloseFlag = APIYNFLAG_NO;
    }
};

//! ί��������Ϣ
struct TapAPIOrderInfo
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��ʺ�

    TAPISTR_10                    ExchangeNo;                            ///< ���������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ�������
    TAPISTR_10                    ContractNo;                            ///< ��Լ1
    TAPISTR_10                    StrikePrice;                        ///< ִ�м۸�1
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ſ���1
    TAPISTR_10                    ContractNo2;                        ///< ��Լ2
    TAPISTR_10                    StrikePrice2;                        ///< ִ�м۸�2
    TAPICallOrPutFlagType        CallOrPutFlag2;                        ///< ���ſ���2

    TAPIOrderTypeType            OrderType;                            ///< ί������
    TAPIOrderSourceType            OrderSource;                        ///< ί����Դ
    TAPITimeInForceType            TimeInForce;                        ///< ί����Ч����
    TAPIDATETIME                ExpireTime;                            ///< ��Ч����(GTD�����ʹ��)

    TAPIYNFLAG                    IsRiskOrder;                        ///< �Ƿ���ձ���
    TAPISideType                OrderSide;                            ///< ��������
    TAPIPositionEffectType        PositionEffect;                        ///< ��ƽ��־1
    TAPIPositionEffectType        PositionEffect2;                    ///< ��ƽ��־2
    TAPISTR_50                    InquiryNo;                            ///< ѯ�ۺ�
    TAPIHedgeFlagType            HedgeFlag;                            ///< Ͷ����ֵ1
    TAPIHedgeFlagType            HedgeFlag2;                            ///< Ͷ����ֵ2
    TAPIREAL64                    OrderPrice;                            ///< ί�м۸�1
    TAPIREAL64                    OrderPrice2;                        ///< ί�м۸�2
    TAPIREAL64                    StopPrice;                            ///< �����۸�
    TAPIUINT32                    OrderQty;                            ///< ί������1
    TAPIUINT32                    OrderQty2;                            ///< ί������2
    TAPIUINT32                    OrderMinQty;                        ///< ��С�ɽ���

    TAPIUINT32                    MinClipSize;                        ///< ��ɽ����С�����
    TAPIUINT32                    MaxClipSize;                        ///< ��ɽ����������

    TAPIINT32                    RefInt;                                ///< ���Ͳο�ֵ
    TAPIREAL64                    RefDouble;                            ///< ����ο�ֵ
    TAPISTR_50                    RefString;                            ///< �ַ����ο�ֵ

    TAPITacticsTypeType            TacticsType;                        ///< ���Ե�����
    TAPITriggerConditionType    TriggerCondition;                    ///< ��������
    TAPITriggerPriceTypeType    TriggerPriceType;                    ///< �����۸�����
    TAPIYNFLAG                    AddOneIsValid;                        ///< �Ƿ�T+1��Ч
    TAPIMarketLevelType            MarketLevel;                        ///< �м۴�����
    TAPIYNFLAG                    FutureAutoCloseFlag;                ///< ��Ȩ���ڻ��Ƿ��ԶԳ�

    TAPIUINT32                    OrderCanceledQty;                    ///< ��������
    TAPISTR_50                    LicenseNo;                            ///< �����Ȩ��
    TAPISTR_20                    ParentAccountNo;                    ///< �ϼ��ʽ��˺�

    TAPICHAR                    ServerFlag;                            ///< ��������ʶ
    TAPISTR_20                    OrderNo;                            ///< ί�б���
    TAPISTR_50                  ClientOrderNo;                        ///< �ͻ��˱���ί�б��
    TAPISTR_20                    OrderLocalNo;                        ///< ���غ�
    TAPISTR_50                    OrderSystemNo;                        ///< ϵͳ��
    TAPISTR_50                    OrderExchangeSystemNo;                ///< ������ϵͳ��
    TAPISTR_10                    TradeNo;                            ///< ���ױ���

    TAPISTR_10                    UpperNo;                            ///< ���ֺ�
    TAPISTR_10                    UpperChannelNo;                        ///< ����ͨ����
    TAPISTR_20                    UpperSettleNo;                        ///< ��Ա�ź������
    TAPISTR_20                    UpperUserNo;                        ///< ���ֵ�¼��
    TAPISTR_20                    OrderInsertUserNo;                    ///< �µ���
    TAPIDATETIME                OrderInsertTime;                    ///< �µ�ʱ��
    TAPISTR_20                    OrderCommandUserNo;                    ///< ¼��������
    TAPISTR_20                    OrderUpdateUserNo;                    ///< ί�и�����
    TAPIDATETIME                OrderUpdateTime;                    ///< ί�и���ʱ��
    TAPIOrderStateType            OrderState;                            ///< ί��״̬

    TAPIREAL64                    OrderMatchPrice;                    ///< �ɽ���1
    TAPIREAL64                    OrderMatchPrice2;                    ///< �ɽ���2
    TAPIUINT32                    OrderMatchQty;                        ///< �ɽ���1
    TAPIUINT32                    OrderMatchQty2;                        ///< �ɽ���2

    TAPIUINT32                    ErrorCode;                            ///< ���һ�β���������Ϣ��
    TAPISTR_50                    ErrorText;                            ///< ������Ϣ

    TAPIYNFLAG                    IsBackInput;                        ///< �Ƿ�Ϊ¼��ί�е�
    TAPIYNFLAG                    IsDeleted;                            ///< ί�гɽ�ɾ�����
    TAPIYNFLAG                    IsAddOne;                            ///< �Ƿ�ΪT+1��

    TAPIUINT32                    OrderStreamID;                        ///< ί����ˮ��
    TAPIUINT32                    UpperStreamID;                        ///< ��������

    TAPIClientIDType            ClientID;                        ///< �ͻ����˺�

    TAPIREAL64                    FeeValue;                            ///< ����������
    TAPIREAL64                    MarginValue;                        ///< ���ᱣ֤��
    TAPISTR_50                    OrderParentSystemNo;                ///< ����ϵͳ��

    TapAPIOrderInfo()
    {
        memset(this, 0, sizeof(TapAPIOrderInfo));
        CallOrPutFlag = TAPI_CALLPUT_FLAG_NONE;
        CallOrPutFlag2 = TAPI_CALLPUT_FLAG_NONE;
        OrderSource = TAPI_ORDER_SOURCE_ESUNNY_API;
        TimeInForce = TAPI_ORDER_TIMEINFORCE_GFD;
        PositionEffect = TAPI_PositionEffect_NONE;
        PositionEffect2 = TAPI_PositionEffect_NONE;
        HedgeFlag = TAPI_HEDGEFLAG_NONE;
        HedgeFlag2 = TAPI_HEDGEFLAG_NONE;
        TacticsType = TAPI_TACTICS_TYPE_NONE;
        AddOneIsValid = APIYNFLAG_NO;
        FutureAutoCloseFlag = APIYNFLAG_NO;
        IsBackInput = APIYNFLAG_NO;
        IsAddOne = APIYNFLAG_NO;
        IsDeleted = APIYNFLAG_NO;
    }
};

//! ��������Ӧ��ṹ
struct TapAPIOrderActionRsp
{
    TAPIORDERACT                ActionType;                            ///< ��������
    TapAPIOrderInfo             OrderInfo;                            ///< ί����Ϣ
};

//! �ͻ��ĵ�����
//! ��������ServerFlag��OrderNo,�Լ�ί�мۺ�ί�����������ֶ���ʱû���á�
struct TapAPIOrderModifyReq
{
    TapAPINewOrder                ReqData;                            ///< ������������
    TAPICHAR                    ServerFlag;                            ///< ��������ʶ
    TAPISTR_20                    OrderNo;                            ///< ί�б��
public:
    TapAPIOrderModifyReq()
    {
        memset(this, 0, sizeof(TapAPIOrderModifyReq));
    }
};

//! �ͻ���������ṹ
//! ��������ServerFlag��OrderNo.
struct TapAPIOrderCancelReq
{
    TAPIINT32                    RefInt;                                ///< ���Ͳο�ֵ
    TAPISTR_50                    RefString;                            ///< �ַ����ο�ֵ
    TAPICHAR                    ServerFlag;                            ///< ��������ʶ
    TAPISTR_20                    OrderNo;                            ///< ί�б���
};

//! ����ί������ṹ
typedef TapAPIOrderCancelReq TapAPIOrderDeactivateReq;

//! ����ί������ṹ
typedef TapAPIOrderCancelReq TapAPIOrderActivateReq;

//! ɾ��ί������ṹ
typedef TapAPIOrderCancelReq TapAPIOrderDeleteReq;

//! ί�в�ѯ����ṹ
struct TapAPIOrderQryReq
{
    TAPIOrderQryTypeType        OrderQryType;                        ///< ί�в�ѯ����
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��ʺţ���ղ��û��������пͻ���
    TAPIUINT32                    DataSeqID;                            ///< ������ʼ����
};

//! ί�����̲�ѯ
struct TapAPIOrderProcessQryReq
{
    TAPICHAR                    ServerFlag;                            ///< ��������ʶ
    TAPISTR_20                    OrderNo;                            ///< ί�б���
};

//! �ɽ���ѯ����ṹ
struct TapAPIFillQryReq
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��ʺţ���ղ��û��������пͻ���
    TAPIUINT32                    DataSeqID;                            ///< ������ʼ����
};

//! �ɽ���Ϣ
struct TapAPIFillInfo
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��ʺ�
    //TAPISTR_20                ParentAccountNo;                    ///< �ϼ��ʽ��˺�
    TAPISTR_10                    ExchangeNo;                            ///< ���������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ�������
    TAPISTR_10                    ContractNo;                            ///< ��Լ
    TAPISTR_10                    StrikePrice;                        ///< ִ�м۸�
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ſ���
    TAPIOrderTypeType            OrderType;                            ///< ί������
    TAPIMatchSourceType            MatchSource;                        ///< �ɽ���Դ
    TAPITimeInForceType            TimeInForce;                        ///< ί����Ч����
    TAPIDATETIME                ExpireTime;                            ///< ��Ч����(GTD�����ʹ��)
    TAPIYNFLAG                    IsRiskOrder;                        ///< �Ƿ���ձ���
    TAPISideType                MatchSide;                            ///< ��������
    TAPIPositionEffectType        PositionEffect;                        ///< ��ƽ��־
    TAPIHedgeFlagType            HedgeFlag;                            ///< Ͷ����ֵ
    TAPICHAR                    ServerFlag;                            ///< ��������ʶ
    TAPISTR_20                    OrderNo;                            ///< ί�б���
    TAPISTR_20                    OrderLocalNo;                        ///< ί�б��غ�
    TAPISTR_20                    MatchNo;                            ///< ���سɽ���
    TAPISTR_70                    ExchangeMatchNo;                    ///< �������ɽ���
    TAPIDATETIME                MatchDateTime;                        ///< �ɽ�ʱ��
    TAPIDATETIME                UpperMatchDateTime;                    ///< ���ֳɽ�ʱ��
    TAPISTR_10                    UpperNo;                            ///< ���ֺ�
    TAPISTR_10                    UpperChannelNo;                        ///< ����ͨ����
    TAPISTR_20                    UpperSettleNo;                        ///< ��Ա�ź��������
    TAPISTR_20                    UpperUserNo;                        ///< ���ֵ�¼��
    TAPISTR_10                    TradeNo;                            ///< ���ױ���
    TAPIREAL64                    MatchPrice;                            ///< �ɽ���
    TAPIUINT32                    MatchQty;                            ///< �ɽ���
    TAPIYNFLAG                    IsBackInput;                        ///< �Ƿ�Ϊ¼��ί�е�
    TAPIYNFLAG                    IsDeleted;                            ///< ί�гɽ�ɾ����
    TAPIYNFLAG                    IsAddOne;                            ///< �Ƿ�ΪT+1��
    TAPIUINT32                    MatchStreamID;                        ///< �ɽ���ˮ��
    TAPIUINT32                  UpperStreamID;                        ///< ��������
    //TAPIOpenCloseModeType        OpenCloseMode;                        ///< ��ƽ��ʽ
    //TAPIREAL64                ContractSize;                        ///< ÿ�ֳ������������
    //TAPISTR_10                CommodityCurrencyGroup;                ///< Ʒ�ֱ�����
    //TAPISTR_10                CommodityCurrency;                    ///< Ʒ�ֱ���
    //TAPICalculateModeType        FeeMode;                            ///< �����Ѽ��㷽ʽ
    //TAPIREAL64                FeeParam;                            ///< �����Ѳ���ֵ ���������Ѿ����տ��������Ѽ���
    TAPISTR_10                    FeeCurrencyGroup;                    ///< �ͻ������ѱ�����
    TAPISTR_10                    FeeCurrency;                        ///< �ͻ������ѱ���
    //TAPIREAL64                PreSettlePrice;                        ///< ������
    TAPIREAL64                    FeeValue;                            ///< ������
    TAPIYNFLAG                    IsManualFee;                        ///< �˹��ͻ������ѱ��
    //TAPIREAL64                Turnover;                            ///< �ɽ����
    TAPIREAL64                    PremiumIncome;                        ///< Ȩ������ȡ
    TAPIREAL64                    PremiumPay;                            ///< Ȩ����֧��
    //TAPISTR_20                OppoMatchNo;                        ///< ���ֱ��سɽ��ţ����ֺ�ƽ�ֶ�Ӧ��ţ�
    TAPIREAL64                    CloseProfit;                        ///< ƽ��ӯ��
    //TAPIREAL64                UnExpProfit;                        ///< δ����ƽӯ
    //TAPIREAL64                UpperMatchPrice;                    ///< ���ֳɽ���
    //TAPIREAL64                QuotePrice;                            ///< ��ǰ�����
    //TAPIREAL64                ClosePL;                            ///< ���ƽӯ
    TAPISTR_50                  OrderSystemNo;                      ///< ί��ϵͳ��
    TAPISTR_70                  UpperMatchNo;                       ///< ���ֳɽ���
    TAPIREAL64                  ClosePositionPrice;                 ///< ָ��ƽ�ֲֳּ۸�
};

//! �ֲֲ�ѯ����ṹ
struct TapAPIPositionQryReq
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��ʺţ���ղ��û��������пͻ���
    TAPIUINT32                    DataSeqID;                            ///< ������ʼ����
};

//! �ֲ���Ϣ
struct TapAPIPositionInfo
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��ʺ�

    TAPISTR_10                    ExchangeNo;                            ///< ���������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ���
    TAPISTR_10                    ContractNo;                            ///< ��Լ
    TAPISTR_10                    StrikePrice;                        ///< ִ�м۸�
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ſ���

    TAPISideType                MatchSide;                            ///< ��������
    TAPIHedgeFlagType            HedgeFlag;                            ///< Ͷ����ֵ
    TAPISTR_70                    PositionNo;                            ///< ���سֲֺ�
    TAPICHAR                    ServerFlag;                            ///< ��������ʶ
    TAPISTR_20                    OrderNo;                            ///< ί�б���
    TAPISTR_20                    MatchNo;                            ///< ���سɽ���
    TAPISTR_70                    ExchangeMatchNo;                    ///< �������ɽ���
    TAPIMatchSourceType            MatchSource;                        ///< �ɽ���Դ
    TAPIDATE                    MatchDate;                            ///< �ɽ�����
    TAPIDATETIME                MatchTime;                            ///< �ɽ�ʱ��
    //TAPIDATETIME                UpperMatchTime;                        ///< ���ֳɽ�ʱ��
    TAPISTR_10                    UpperNo;                            ///< ���ֺ�
    TAPISTR_20                    UpperSettleNo;                        ///< ��Ա�ź��������
    TAPISTR_20                    UpperUserNo;                        ///< ���ֵ�¼��
    TAPISTR_10                    TradeNo;                            ///< ���ױ���
    TAPIREAL64                    PositionPrice;                        ///< �ֲּ�
    TAPIUINT32                    PositionQty;                        ///< �ֲ���
    TAPIYNFLAG                    IsBackInput;                        ///< �Ƿ�Ϊ¼��ί�е�
    TAPIYNFLAG                    IsAddOne;                            ///< �Ƿ�ΪT+1��
    TAPIUINT32                    MatchStreamID;                        ///< �ɽ���ˮ��
    TAPIUINT32                    PositionStreamId;                    ///< �ֲ�����
    //TAPIOpenCloseModeType        OpenCloseMode;                        ///< ��ƽ��ʽ
    TAPIREAL64                    ContractSize;                        ///< ÿ�ֳ������������
    TAPISTR_10                    CommodityCurrencyGroup;                ///< Ʒ�ֱ�����
    TAPISTR_10                    CommodityCurrency;                    ///< Ʒ�ֱ���
    TAPIREAL64                    PreSettlePrice;                        ///< ������
    TAPIREAL64                  SettlePrice;                        ///< ��ǰ����۸�
    TAPIREAL64                    Turnover;                            ///< �ֲֽ��
    //TAPICalculateModeType        AccountMarginMode;                    ///< ��֤����㷽ʽ
    //TAPIREAL64                AccountMarginParam;                    ///< ��֤�����ֵ
    //TAPICalculateModeType        UpperMarginMode;                    ///< ��֤����㷽ʽ
    //TAPIREAL64                UpperMarginParam;                    ///< ��֤�����ֵ
    TAPIREAL64                    AccountInitialMargin;                ///< �ͻ���ʼ��֤��
    TAPIREAL64                    AccountMaintenanceMargin;            ///< �ͻ�ά�ֱ�֤��
    TAPIREAL64                  UpperInitialMargin;                    ///< ���ֳ�ʼ��֤��
    TAPIREAL64                  UpperMaintenanceMargin;                ///< ����ά�ֱ�֤��
    TAPIREAL64                    PositionProfit;                        ///< �ֲ�ӯ��
    TAPIREAL64                    LMEPositionProfit;                    ///< LME�ֲ�ӯ��
    TAPIREAL64                    OptionMarketValue;                    ///< ��Ȩ��ֵ
    TAPISTR_20                    MatchCmbNo;                            ///< ��ϳֲֺ�
    TAPIYNFLAG                    IsHistory;                            ///< �Ƿ���ʷ�ֲ�
    TAPIREAL64                    FloatingPL;                            ///< ��ʸ�ӯ
    TAPIREAL64                    CalculatePrice;                        ///< ����۸�

    TapAPIPositionInfo()
    {
        memset(this, 0, sizeof(TapAPIPositionInfo));
        IsBackInput = APIYNFLAG_NO;
        IsAddOne = APIYNFLAG_NO;
        IsHistory = APIYNFLAG_NO;
    }
};

//! �ֲֻ�����Ϣ
struct TapAPIPositionSumInfo
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��ʺ�

    TAPISTR_10                    ExchangeNo;                            ///< ���������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ���
    TAPISTR_10                    ContractNo;                            ///< ��Լ
    TAPISTR_10                    StrikePrice;                        ///< ִ�м۸�
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ſ���

    TAPISideType                MatchSide;                            ///< ��������
    TAPIHedgeFlagType            HedgeFlag;                            ///< Ͷ����ֵ
    
    TAPIREAL64                    PositionPrice;                        ///< �ֲ־��ۡ�
    TAPIUINT32                    PositionQty;                        ///< �ֲ���
    TAPIUINT32                    HisPositionQty;                        ///< ��ʷ�ֲ���
};

//! �ͻ��ֲ�ӯ��
struct TapAPIPositionProfit
{
    TAPISTR_70                    PositionNo;                            ///< ���سֲֺ�
    TAPIUINT32                    PositionStreamId;                    ///< �ֲ�����
    TAPIREAL64                    PositionProfit;                        ///< �ֲ�ӯ��
    TAPIREAL64                    LMEPositionProfit;                    ///< LME�ֲ�ӯ��
    TAPIREAL64                    OptionMarketValue;                    ///< ��Ȩ��ֵ
    TAPIREAL64                    CalculatePrice;                        ///< ����۸�
    TAPIREAL64                    FloatingPL;                            ///< ��ʸ�ӯ
};

//! �ͻ��ֲ�ӯ��֪ͨ
struct TapAPIPositionProfitNotice
{
    TAPIYNFLAG                    IsLast;                                ///< �Ƿ����һ��
    TapAPIPositionProfit*        Data;                                ///< �ͻ��ֲ�ӯ����Ϣ
};

//! ƽ�ֲ�ѯ����ṹ
struct TapAPICloseQryReq
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��ʺţ���ղ��û��������пͻ���
    TAPIUINT32                    DataSeqID;                            ///< ������ʼ����
};

//! ƽ����Ϣ
struct TapAPICloseInfo
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��ʺ�
    //TAPISTR_20                ParentAccountNo;                    ///< �ϼ��ʽ��˺�
    TAPISTR_10                    ExchangeNo;                            ///< ���������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ���
    TAPISTR_10                    ContractNo;                            ///< ��Լ
    TAPISTR_10                    StrikePrice;                        ///< ִ�м۸�
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ſ���
    //TAPISTR_10                OpenOrderExchangeNo;                ///< ���������
    //TAPICommodityType            OpenOrderCommodityType;                ///< Ʒ������
    //TAPISTR_10                OpenOrderCommodityNo;                ///< Ʒ�ֱ�������
    //TAPISTR_10                CloseOrderExchangeNo;                ///< ���������
    //TAPICommodityType            CloseOrderCommodityType;            ///< Ʒ������
    //TAPISTR_10                CloseOrderCommodityNo;                ///< Ʒ�ֱ�������
    TAPIMatchSourceType            OpenMatchSource;      ///< �ɽ���Դ
    TAPIMatchSourceType            CloseMatchSource;     ///< �ɽ���Դ
    TAPISideType                CloseSide;                            ///< ƽ��һ�ߵ���������
    TAPIUINT32                    CloseQty;                            ///< ƽ�ֳɽ���
    TAPIREAL64                    OpenPrice;                            ///< ���ֳɽ���
    TAPIREAL64                    ClosePrice;                            ///< ƽ�ֳɽ���
    TAPICHAR                    OpenServerFlag;                        ///< ��������ʶ
    TAPISTR_20                    OpenOrderNo;                        ///< ί�б���
    TAPISTR_20                    OpenMatchNo;                        ///< ���سɽ���
    TAPISTR_70                    OpenExchangeMatchNo;                ///< �������ɽ���
    TAPIDATETIME                OpenMatchDateTime;                    ///< �ɽ�ʱ��
    TAPICHAR                    CloseServerFlag;                    ///< ��������ʶ
    TAPISTR_20                    CloseOrderNo;                        ///< ί�б���
    TAPISTR_20                    CloseMatchNo;                        ///< ���سɽ���
    TAPISTR_70                    CloseExchangeMatchNo;                ///< �������ɽ���
    TAPIDATETIME                CloseMatchDateTime;                    ///< �ɽ�ʱ��
    TAPIUINT32                  CloseStreamId;                        ///< ƽ������
    //TAPIOpenCloseModeType        OpenCloseMode;                        ///< ��ƽ��ʽ
    TAPIREAL64                    ContractSize;                        ///< ÿ�ֳ������������
    //TAPISTR_10                CommodityCurrencyGroup;                ///< Ʒ�ֱ�����
    //TAPISTR_10                CommodityCurrency;                    ///< Ʒ�ֱ���
    TAPIREAL64                    PreSettlePrice;                        ///< ������
    //TAPIREAL64                PremiumIncome;                        ///< Ȩ������ȡ
    //TAPIREAL64                PremiumPay;                            ///< Ȩ����֧��
    TAPIREAL64                    CloseProfit;                        ///< ƽ��ӯ��
    TAPIREAL64                    UnExpProfit;                        ///< δ����ƽӯ
    TAPIREAL64                    ClosePL;                            ///< ���ƽӯ
};

//! �ʽ��ѯ����
struct TapAPIFundReq
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��ʺ�
    TAPIUINT32                    DataSeqID;                            ///< ���ݲ�ѯ��ʼ���ţ�1��ʾ��һ�����ݣ����β�ѯ���������ŵ����ݣ�
};

//! �ʽ��˺��ʽ���Ϣ
struct TapAPIFundData
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��˺�
    //TAPISTR_20                ParentAccountNo;                    ///< �ϼ��ʽ��˺�
    TAPISTR_10                    CurrencyGroupNo;                    ///< �������
    TAPISTR_10                    CurrencyNo;                            ///< ���ֺ�(Ϊ�ձ�ʾ����������ʽ�)
    TAPIREAL64                    TradeRate;                            ///< ���׻���
    TAPIFutureAlgType            FutureAlg;                            ///< �ڻ��㷨
    TAPIOptionAlgType            OptionAlg;                            ///< ��Ȩ�㷨
    TAPIREAL64                    PreBalance;                            ///< ���ս��
    TAPIREAL64                    PreUnExpProfit;                        ///< ����δ����ƽӯ
    TAPIREAL64                    PreLMEPositionProfit;                ///< ����LME�ֲ�ƽӯ
    TAPIREAL64                    PreEquity;                            ///< ����Ȩ��
    TAPIREAL64                    PreAvailable1;                        ///< ���տ���
    TAPIREAL64                    PreMarketEquity;                    ///< ������ֵȨ��
    TAPIREAL64                    CashInValue;                        ///< ���
    TAPIREAL64                    CashOutValue;                        ///< ����
    TAPIREAL64                    CashAdjustValue;                    ///< �ʽ����
    TAPIREAL64                    CashPledged;                        ///< ��Ѻ�ʽ�
    TAPIREAL64                    FrozenFee;                            ///< ����������
    TAPIREAL64                    FrozenDeposit;                        ///< ���ᱣ֤��
    TAPIREAL64                    AccountFee;                            ///< �ͻ������Ѱ�������������
    TAPIREAL64                    ExchangeFee;                        ///< ���������
    TAPIREAL64                    AccountDeliveryFee;                    ///< �ͻ�����������
    TAPIREAL64                    PremiumIncome;                        ///< Ȩ������ȡ
    TAPIREAL64                    PremiumPay;                            ///< Ȩ����֧��
    TAPIREAL64                    CloseProfit;                        ///< ƽ��ӯ��
    TAPIREAL64                    DeliveryProfit;                        ///< ����ӯ��
    TAPIREAL64                    UnExpProfit;                        ///< δ����ƽӯ
    TAPIREAL64                    ExpProfit;                            ///< ����ƽ��ӯ��
    TAPIREAL64                    PositionProfit;                        ///< ����LME�ֲ�ӯ��
    TAPIREAL64                    LmePositionProfit;                    ///< LME�ֲ�ӯ��
    TAPIREAL64                    OptionMarketValue;                    ///< ��Ȩ��ֵ
    TAPIREAL64                    AccountInitialMargin;                ///< �ͻ���ʼ��֤��
    TAPIREAL64                    AccountMaintenanceMargin;            ///< �ͻ�ά�ֱ�֤��
    TAPIREAL64                    UpperInitialMargin;                    ///< ���ֳ�ʼ��֤��
    TAPIREAL64                    UpperMaintenanceMargin;                ///< ����ά�ֱ�֤��
    TAPIREAL64                    Discount;                            ///< LME����
    TAPIREAL64                    Balance;                            ///< ���ս��
    TAPIREAL64                    Equity;                                ///< ����Ȩ��
    TAPIREAL64                    Available;                            ///< ���տ���
    TAPIREAL64                    CanDraw;                            ///< ����ȡ
    TAPIREAL64                    MarketEquity;                        ///< �˻���ֵ
    TAPIREAL64                    AuthMoney;                            ///< �����ʽ�
    TAPIREAL64                    OriginalCashInOut;                    ///< ����ԭʼ�����
    TAPIREAL64                    FloatingPL;                            ///< ��ʸ�ӯ
    TAPIREAL64                    FrozenRiskFundValue;                ///< ���ն����ʽ�
    TAPIREAL64                    ClosePL;                            ///< ���ƽӯ
    TAPIREAL64                    NoCurrencyPledgeValue;                ///< �ǻ�����Ѻ
    TAPIREAL64                    PrePledgeValue;                        ///< �ڳ���Ѻ
    TAPIREAL64                    PledgeIn;                            ///< ����
    TAPIREAL64                    PledgeOut;                            ///< �ʳ�
    TAPIREAL64                    PledgeValue;                        ///< ��Ѻ���
    TAPIREAL64                    BorrowValue;                        ///< ���ý��
    TAPIREAL64                    SpecialAccountFrozenMargin;            ///< �����Ʒ���ᱣ֤��
    TAPIREAL64                    SpecialAccountMargin;                ///< �����Ʒ��֤��
    TAPIREAL64                    SpecialAccountFrozenFee;            ///< �����Ʒ����������
    TAPIREAL64                    SpecialAccountFee;                    ///< �����Ʒ������
    TAPIREAL64                    SpecialFloatProfit;                    ///< �����Ʒ��ӯ
    TAPIREAL64                    SpecialCloseProfit;                    ///< �����Ʒƽӯ
    TAPIREAL64                    SpecialFloatPL;                        ///< �����Ʒ��ʸ�ӯ
    TAPIREAL64                    SpecialClosePL;                        ///< �����Ʒ���ƽӯ
    TAPIREAL64                    RiskRate;                            ///< ������
};

//! ������ѯ��֪ͨ�ṹ
struct TapAPIReqQuoteNotice
{
    TAPISTR_10                    ExchangeNo;                            ///< ���������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ���
    TAPISTR_10                    ContractNo;                            ///< ��Լ
    TAPISTR_10                    StrikePrice;                        ///< ִ�м۸�
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ſ���
    TAPISTR_50                    InquiryNo;                            ///< ѯ�ۺ�
    TAPIDATETIME                UpdateTime;                            ///< ����ʱ��
};

//! ���������Ϣ(������ר��)
struct TapAPIDeepQuoteInfo
{
    TAPISideType                Side;                                ///< ��������
    TAPIREAL64                    Price;                                ///< �ҵ��۸�
    TAPIUINT32                    Qty;                                ///< �ҵ�����
};

//! ��������ѯӦ��(������ר��)
struct TapAPIDeepQuoteQryRsp
{
    TapAPIContract                Contract;                            ///< ��Լ
    TapAPIDeepQuoteInfo            DeepQuote;                            ///< �������
};

//! ������ʱ��״̬��Ϣ��ѯ����ṹ(������ר��)
struct TapAPIExchangeStateInfoQryReq
{
};

//! ������ʱ��״̬��Ϣ(������ר��)
struct TapAPIExchangeStateInfo
{
    TAPISTR_10                    UpperChannelNo;                        ///< ����ͨ�����
    TAPISTR_10                    ExchangeNo;                            ///< ���������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ��
    TAPIDATETIME                ExchangeTime;                        ///< ������ʱ��
    TAPITradingStateType        TradingState;                        ///< ������״̬
};

//! ������ʱ��״̬��Ϣ֪ͨ�ṹ(������ר��)
struct TapAPIExchangeStateInfoNotice
{
    TAPIYNFLAG                    IsLast;                                ///< �Ƿ����һ������
    TapAPIExchangeStateInfo        ExchangeStateInfo;                    ///< ������ʱ��״̬��Ϣ
};

//! ����ͨ����Ϣ��ѯ����ṹ(������ר��)
struct TapAPIUpperChannelQryReq
{
};

//! ����ͨ����Ϣ�ṹ(������ר��)
struct TapAPIUpperChannelInfo
{
    TAPISTR_10                    UpperChannelNo;                        ///< ����ͨ�����
    TAPISTR_20                    UpperChannelName;                    ///< ����ͨ������
    TAPISTR_10                    UpperNo;                            ///< ����ͨ����
    TAPISTR_20                    UpperUserNo;                        ///< ����ϯλ��
};

//! �ͻ����շ��ʲ�ѯ����ṹ
struct TapAPIAccountRentQryReq
{
    TAPISTR_20                    AccountNo;                            ///< �ʽ��˻�
    TAPISTR_10                    ExchangeNo;                            ///< ����������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ��
    TAPISTR_10                    ContractNo;                            ///< ��Լ����
};

//! �ͻ����շ�����Ϣ�ṹ
struct    TapAPIAccountRentInfo
{
    TAPISTR_20                    AccountNo;                            ///< �ʽ��˻�
    TAPISTR_10                    ExchangeNo;                            ///< ����������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ��
    TAPISTR_10                    ContractNo;                            ///< ��Լ����
    TAPIMatchSourceType            MatchSource;                        ///< �ɽ���Դ
    TAPISTR_10                    CurrencyNo;                            ///< ���ֱ��

    TAPICalculateModeType        FeeMode;                            ///< �����Ѽ��㷽ʽ
    TAPIREAL64                    OpenTurnover;                        ///< ���������Ѱ����
    TAPIREAL64                    ClosedTurnover;                        ///< ƽ�������Ѱ����
    TAPIREAL64                    CloseNewTurnover;                    ///< ƽ�������Ѱ����
    TAPIREAL64                    OpenVolume;                            ///< ���������Ѱ�����
    TAPIREAL64                    ClosedVolume;                        ///< ƽ�������Ѱ�����
    TAPIREAL64                    CloseNewVolume;                        ///< ƽ�������Ѱ�����

    TAPICalculateModeType        MarginMode;                            ///< ��֤����㷽ʽ
    TAPIREAL64                    BuyTInitMargin;                        ///< ��Ͷ����ʼ��֤��
    TAPIREAL64                    SellTInitMargin;                    ///< ��Ͷ����ʼ��֤��
    TAPIREAL64                    BuyBInitMargin;                        ///< ��ֵ��ʼ��֤��
    TAPIREAL64                    SellBInitMargin;                    ///< ����ֵ��ʼ��֤��
    TAPIREAL64                    BuyLInitMargin;                        ///< ��������ʼ��֤��
    TAPIREAL64                    SellLInitMargin;                    ///< ��������ʼ��֤��
    TAPIREAL64                    BuyMInitMargin;                        ///< �������̳�ʼ��֤��
    TAPIREAL64                    SellMInitMargin;                    ///< �������̳�ʼ��֤��
    TAPIREAL64                    BuyTMaintMargin;                    ///< ��Ͷ��ά�ֱ�֤��
    TAPIREAL64                    SellTMaintMargin;                    ///< ��Ͷ��ά�ֱ�֤��
    TAPIREAL64                    BuyBMaintMargin;                    ///< ��ֵά�ֱ�֤��
    TAPIREAL64                    SellBMaintMargin;                    ///< ����ֵά�ֱ�֤��
    TAPIREAL64                    BuyLMaintMargin;                    ///< ������ά�ֱ�֤��
    TAPIREAL64                    SellLMaintMargin;                    ///< ������ά�ֱ�֤��
    TAPIREAL64                    BuyMMaintMargin;                    ///< ��������ά�ֱ�֤��
    TAPIREAL64                    SellMMaintMargin;                    ///< ��������ά�ֱ�֤��
};

//! ���ױ�����Ϣ(������ר��)
struct TapAPICurrencyInfo
{
    TAPISTR_10                    CurrencyNo;                        ///< ���ֱ��
    TAPISTR_10                    CurrencyGroupNo;                ///< ��������
    TAPIREAL64                    TradeRate;                        ///< ���׻���
    TAPIREAL64                    TradeRate2;                        ///< ���׻���2

    TAPIFutureAlgType            FutureAlg;                        ///< �ڻ��㷨
    TAPIOptionAlgType            OptionAlg;                        ///< ��Ȩ�㷨
};

//! ������Ϣ��ѯ�ṹ(�����ǡ�������ר��)
struct TapAPITradeMessageQryReq
{
    TAPIUINT32                    SerialID;                        ///< ����
    TAPIMsgQryTypeType          TradeMsgQryType;                ///< ��ѯ����(������ר�ã�������Ĭ��Ϊȫ��)
    TAPISTR_20                    AccountNo;                        ///< �ͻ��ʽ��˺�
    TAPIDATETIME                BeginSendDateTime;              ///< ��ʼʱ��
    TAPIDATETIME                EndSendDateTime;                ///< ����ʱ��
};

//! ������Ϣ�ṹ(�����ǡ�������ר��)
struct TapAPITradeMessage
{
    TAPIUINT32                    SerialID;                        ///< ����
    TAPISTR_20                    AccountNo;                        ///< �ͻ��ʽ��˺�

    TAPIDATETIME                TMsgValidDateTime;                ///< ��Ϣ��Чʱ��
    TAPISTR_50                    TMsgTitle;                        ///< ��Ϣ����
    TAPISTR_500                    TMsgContent;                    ///< ��Ϣ����
    TAPIMsgTypeType                TMsgType;                        ///< ��Ϣ����
    TAPIMsgLevelType            TMsgLevel;                        ///< ��Ϣ����

    TAPIYNFLAG                    IsSendBySMS;                    ///< �Ƿ��Ͷ���
    TAPIYNFLAG                    IsSendByEMail;                    ///< �Ƿ����ʼ�
    TAPISTR_20                    Sender;                            ///<������
    TAPIDATETIME                SendDateTime;                    ///< ����ʱ��
};

//! �ͻ��ʽ������ѯ����ṹ(������ר��)
struct TapAPIAccountCashAdjustQryReq
{
    TAPIUINT32                    SerialID;                 ///< ����
    TAPISTR_20                    AccountNo;                ///< �ͻ��ʽ��˺�
    TAPISTR_20                    AccountAttributeNo;          ///< �ͻ�����
    TAPIDATE                    BeginDate;                  ///< ��ʼ����(����)
    TAPIDATE                    EndDate;                  ///< ��������(����)
};

//! �ͻ��ʽ������ѯӦ��ṹ(������ר��)
struct TapAPIAccountCashAdjustQryRsp
{
    TAPIDATE                    Date;                            ///< ����
    TAPISTR_20                    AccountNo;                        ///< �ͻ��ʽ��˺�

    TAPICashAdjustTypeType        CashAdjustType;                    ///< �ʽ��������
    TAPISTR_10                    CurrencyGroupNo;                ///< �������
    TAPISTR_10                    CurrencyNo;                        ///< ���ֺ�
    TAPIREAL64                    CashAdjustValue;                ///< �ʽ�������
    TAPISTR_100                    CashAdjustRemark;                ///< �ʽ������ע

    TAPIDATETIME                OperateTime;                    ///< ����ʱ��
    TAPISTR_20                    OperatorNo;                        ///< ����Ա

    TAPISTR_10                    AccountBank;                    ///< �ͻ�����
    TAPISTR_20                    BankAccount;                    ///< �ͻ������˺�
    TAPIBankAccountLWFlagType    AccountLWFlag;                    ///< �ͻ�����ұ�ʶ
    TAPISTR_10                    CompanyBank;                    ///< ��˾����
    TAPISTR_20                    InternalBankAccount;            ///< ��˾�����˻�
    TAPIBankAccountLWFlagType    CompanyLWFlag;                    ///< ��˾����ұ�ʶ
};

//! �ͻ��˵���ѯ����ṹ(�����ǡ�������ר��)
struct TapAPIBillQryReq
{
    TAPISTR_20                    UserNo;             ///< �û����
    TAPIBillTypeType            BillType;           ///< �˵�����
    TAPIDATE                    BillDate;           ///< �˵�����
    TAPIBillFileTypeType        BillFileType;       ///< �ʵ��ļ�����
};

//! �ͻ��˵���ѯӦ��ṹ(�����ǡ�������ר��)
struct TapAPIBillQryRsp
{
    TapAPIBillQryReq            Reqdata;      ///< �˵���ѯ��������
    TAPIINT32                    BillLen;      ///< �˵��ļ�����
    TAPICHAR                    BillText[1];  ///< �䳤�˵����ݣ�������BillLenָ��
};

//! ��ʷί�в�ѯ����ṹ(������ר��)
struct TapAPIHisOrderQryReq
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��˺�
    TAPISTR_20                    AccountAttributeNo;                    ///< �ͻ����Ժ�
    TAPIDATE                    BeginDate;                            ///< ��ʼʱ�� (����)
    TAPIDATE                    EndDate;                            ///< ����ʱ�� (����)
};

//! ��ʷί�в�ѯӦ��ṹ(������ר��)
struct TapAPIHisOrderQryRsp
{
    TAPIDATE                    Date;                                ///< ����
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��˺�

    TAPISTR_10                    ExchangeNo;                            ///< ���������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ���
    TAPISTR_10                    ContractNo;                            ///< ��Լ1
    TAPISTR_10                    StrikePrice;                        ///< ִ�м۸�1
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ſ���
    TAPISTR_10                    ContractNo2;                        ///< ��Լ2
    TAPISTR_10                    StrikePrice2;                        ///< ִ�м۸�2
    TAPICallOrPutFlagType        CallOrPutFlag2;                        ///< ���ſ���2

    TAPIOrderTypeType            OrderType;                            ///< ί������
    TAPIOrderSourceType            OrderSource;                        ///< ί����Դ
    TAPITimeInForceType            TimeInForce;                        ///< ί����Ч����
    TAPIDATETIME                ExpireTime;                            ///< ��Ч����(GTD�����ʹ��)
    TAPIYNFLAG                    IsRiskOrder;                        ///< �Ƿ���ձ���
    TAPISideType                OrderSide;                            ///< ��������
    TAPIPositionEffectType        PositionEffect;                        ///< ��ƽ��־
    TAPIPositionEffectType        PositionEffect2;                    ///< ��ƽ��־2
    TAPISTR_50                    InquiryNo;                            ///< ѯ�ۺ�
    TAPIHedgeFlagType            HedgeFlag;                            ///< Ͷ����ֵ
    TAPIREAL64                    OrderPrice;                            ///< ί�м۸�
    TAPIREAL64                    OrderPrice2;                        ///< ί�м۸�2
    TAPIREAL64                    StopPrice;                            ///< �����۸�
    TAPIUINT32                    OrderQty;                            ///< ί������
    TAPIUINT32                    OrderMinQty;                        ///< ��С�ɽ���
    TAPIUINT32                    OrderCanceledQty;                    ///< ��������

    TAPIINT32                    RefInt;                                ///< ���Ͳο�ֵ
    TAPIREAL64                    RefDouble;                            ///<����ο���
    TAPISTR_50                    RefString;                            ///< �ַ����ο�ֵ

    TAPICHAR                    ServerFlag;                            ///< ��������ʶ
    TAPISTR_20                    OrderNo;                            ///< ί�б���
    TAPIUINT32                    OrderStreamID;                        ///< ί����ˮ��

    TAPISTR_10                    UpperNo;                            ///< ���ֺ�
    TAPISTR_10                    UpperChannelNo;                        ///< ����ͨ�����
    TAPISTR_20                    OrderLocalNo;                        ///< ���غ�
    TAPIUINT32                    UpperStreamID;                        ///< ��������

    TAPISTR_50                    OrderSystemNo;                        ///< ϵͳ��
    TAPISTR_50                    OrderExchangeSystemNo;                ///< ������ϵͳ��
    TAPISTR_50                    OrderParentSystemNo;                ///< ����ϵͳ��

    TAPISTR_20                    OrderInsertUserNo;                    ///< �µ���
    TAPIDATETIME                OrderInsertTime;                    ///< �µ�ʱ��
    TAPISTR_20                    OrderCommandUserNo;                    ///< ָ���´���
    TAPISTR_20                    OrderUpdateUserNo;                    ///< ί�и�����
    TAPIDATETIME                OrderUpdateTime;                    ///< ί�и���ʱ��

    TAPIOrderStateType            OrderState;                            ///< ί��״̬

    TAPIREAL64                    OrderMatchPrice;                    ///< �ɽ���
    TAPIREAL64                    OrderMatchPrice2;                    ///< �ɽ���2
    TAPIUINT32                    OrderMatchQty;                        ///< �ɽ���
    TAPIUINT32                    OrderMatchQty2;                        ///< �ɽ���2

    TAPIUINT32                    ErrorCode;                            ///< ���һ�β���������Ϣ��
    TAPISTR_50                    ErrorText;                            ///< ������Ϣ

    TAPIYNFLAG                    IsBackInput;                        ///< �Ƿ�Ϊ¼��ί�е�
    TAPIYNFLAG                    IsDeleted;                            ///< ί�гɽ�ɾ�����
    TAPIYNFLAG                    IsAddOne;                            ///< �Ƿ�ΪT+1��
    TAPIYNFLAG                    AddOneIsValid;                        ///< �Ƿ�T+1��Ч

    TAPIUINT32                    MinClipSize;                        ///< ��ɽ����С�����
    TAPIUINT32                    MaxClipSize;                        ///< ��ɽ����������
    TAPISTR_50                    LicenseNo;                            ///< �����Ȩ��

    TAPITacticsTypeType            TacticsType;                        ///< ���Ե�����
    TAPITriggerConditionType    TriggerCondition;                    ///< ��������
    TAPITriggerPriceTypeType    TriggerPriceType;                    ///< �����۸�����
};

//! ��ʷ�ɽ���ѯ����ṹ(������ר��)
struct TapAPIHisFillQryReq
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��˺�
    TAPISTR_20                    AccountAttributeNo;                    ///< �ͻ����Ժ�
    TAPIDATE                    BeginDate;                            ///< ��ʼ���ڣ�����
    TAPIDATE                    EndDate;                            ///< �������ڣ�����
    TAPICHAR                    CountType;                            ///< ͳ������
};

//! ��ʷ�ɽ���ѯӦ��ṹ(������ר��)
//! key1=SerialID
//! key2=ExchangeNo+MatchCmbNo+MatchNo+MatchSide
struct TapAPIHisFillQryRsp
{
    TAPIDATE                    SettleDate;                            ///< ��������
    TAPIDATE                    TradeDate;                            ///<��������
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��˺�

    TAPISTR_10                    ExchangeNo;                            ///< �г����߽���������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֺ�
    TAPISTR_10                    ContractNo;                            ///< ��Լ��
    TAPISTR_10                    StrikePrice;                        ///< ִ�м�
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ǿ�����־

    TAPIMatchSourceType            MatchSource;                        ///< �ɽ���Դ
    TAPISideType                MatchSide;                            ///< ��������
    TAPIPositionEffectType        PositionEffect;                        ///< ��ƽ��־
    TAPIHedgeFlagType            HedgeFlag;                            ///< Ͷ����ֵ
    TAPIREAL64                    MatchPrice;                            ///< �ɽ���
    TAPIUINT32                    MatchQty;                            ///< �ɽ���

    TAPISTR_20                    OrderNo;                            ///< ί�к�
    TAPISTR_20                    MatchNo;                            ///< �ɽ����
    TAPIUINT32                    MatchStreamID;                        ///< �ɽ���ˮ��

    TAPISTR_10                    UpperNo;                            ///< ���ֺ�
    TAPISTR_20                    MatchCmbNo;                            ///< ��Ϻ�
    TAPISTR_70                    ExchangeMatchNo;                    ///< �ɽ����(�������ɽ���)
    TAPIUINT32                    MatchUpperStreamID;                    ///< ������ˮ��

    TAPISTR_10                    CommodityCurrencyGroup;             ///< Ʒ�ֱ�����
    TAPISTR_10                    CommodityCurrency;                    ///< Ʒ�ֱ���

    TAPIREAL64                    Turnover;                            ///< �ɽ����
    TAPIREAL64                    PremiumIncome;                        ///< Ȩ��������
    TAPIREAL64                    PremiumPay;                            ///< Ȩ����֧��

    TAPIREAL64                    AccountFee;                            ///< �ͻ�������
    TAPISTR_10                    AccountFeeCurrencyGroup;            ///< �ͻ������ѱ�����
    TAPISTR_10                    AccountFeeCurrency;                    ///< �ͻ������ѱ���
    TAPIYNFLAG                    IsManualFee;                        ///< �˹��ͻ������ѱ��
    TAPIREAL64                    AccountOtherFee;                    ///< �ͻ���������

    TAPIREAL64                    UpperFee;                            ///< ����������
    TAPISTR_10                    UpperFeeCurrencyGroup;              ///< ���������ѱ�����
    TAPISTR_10                    UpperFeeCurrency;                    ///< ���������ѱ���
    TAPIYNFLAG                    IsUpperManualFee;                    ///< �˹����������ѱ��
    TAPIREAL64                    UpperOtherFee;                        ///< ������������

    TAPIDATETIME                MatchDateTime;                        ///< �ɽ�ʱ��
    TAPIDATETIME                UpperMatchDateTime;                    ///< ���ֳɽ�ʱ��

    TAPIREAL64                    CloseProfit;                        ///< ƽ��ӯ��
    TAPIREAL64                    ClosePrice;                            ///< ָ��ƽ�ּ۸�

    TAPIUINT32                    CloseQty;                            ///< ƽ����

    TAPISTR_10                    SettleGroupNo;                        ///<�������
    TAPISTR_20                    OperatorNo;                            ///< ����Ա
    TAPIDATETIME                OperateTime;                        ///< ����ʱ��
};

//! ��ʷί�����̲�ѯ����ṹ(������ר��)
struct TapAPIHisOrderProcessQryReq
{
    TAPIDATE                    Date;             ///< ����
    TAPISTR_20                    OrderNo;          ///< ί�к�
};

//! ��ʷί�����̲�ѯӦ�����ݽṹ(������ר��)
typedef TapAPIHisOrderQryRsp        TapAPIHisOrderProcessQryRsp;

//! ��ʷ�ֲֲ�ѯ����ṹ(������ר��)
struct TapAPIHisPositionQryReq
{
    TAPISTR_20                    AccountNo;                        ///< �ͻ��ʽ��˺�
    TAPIDATE                    Date;                            ///< ����
    TAPISettleFlagType          SettleFlag;                      ///< ��������
};

//! ��ʷ�ֲֲ�ѯ����Ӧ��ṹ(������ר��)
//! key1=SerialID
//! key2=SettleDate+ExchangeNo+PositionNo+MatchSide
struct TapAPIHisPositionQryRsp
{
    TAPIDATE                    SettleDate;                            ///< ��������
    TAPIDATE                    OpenDate;                            ///< ��������

    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��˺�

    TAPISTR_10                    ExchangeNo;                            ///< �г����߽���������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ���
    TAPISTR_10                    ContractNo;                            ///< ��Լ��
    TAPISTR_10                    StrikePrice;                        ///< ִ�м�
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ǿ�����־

    TAPISideType                MatchSide;                            ///< ��������
    TAPIHedgeFlagType            HedgeFlag;                            ///< Ͷ����ֵ
    TAPIREAL64                    PositionPrice;                        ///< �ֲּ۸�
    TAPIUINT32                    PositionQty;                        ///< �ֲ���

    TAPISTR_20                    OrderNo;                            ///< ί�к�
    TAPISTR_70                    PositionNo;                            ///< �ֱֲ��

    TAPISTR_10                    UpperNo;                            ///< ���ֺ�

    TAPISTR_10                    CurrencyGroup;                        ///< Ʒ�ֱ�����
    TAPISTR_10                    Currency;                            ///< Ʒ�ֱ���

    TAPIREAL64                    PreSettlePrice;                        ///< ���ս���۸�
    TAPIREAL64                    SettlePrice;                        ///< ����۸�
    TAPIREAL64                    PositionDProfit;                    ///< �ֲ�ӯ��(����)
    TAPIREAL64                    LMEPositionProfit;                    ///< LME�ֲ�ӯ��
    TAPIREAL64                    OptionMarketValue;                    ///< ��Ȩ��ֵ

    TAPIREAL64                    AccountInitialMargin;                ///< �ͻ���ʼ��֤��
    TAPIREAL64                    AccountMaintenanceMargin;            ///< �ͻ�ά�ֱ�֤��
    TAPIREAL64                    UpperInitialMargin;                    ///< ���ֳ�ʼ��֤��
    TAPIREAL64                    UpperMaintenanceMargin;                ///< ����ά�ֱ�֤��

    TAPISTR_10                    SettleGroupNo;                        ///< �������
};

//! �����ѯ����ṹ(������ר��)
struct TapAPIHisDeliveryQryReq
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��˺�
    TAPISTR_20                    AccountAttributeNo;                    ///< �ͻ����Ժ�
    TAPIDATE                    BeginDate;                            ///< ��ʼ���ڣ����
    TAPIDATE                    EndDate;                            ///< �������ڣ����
    TAPICHAR                    CountType;                            ///< ͳ������
};

//! �����ѯӦ�����ݽṹ(������ר��)
//! key1=SerialID
struct TapAPIHisDeliveryQryRsp
{
    TAPIDATE                    DeliveryDate;                        ///< ��������
    TAPIDATE                    OpenDate;                            ///< ��������
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��˺�

    TAPISTR_10                    ExchangeNo;                            ///< �г��Ż���������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ���
    TAPISTR_10                    ContractNo;                            ///< ��Լ����
    TAPISTR_10                    StrikePrice;                        ///< ִ�м�
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ǿ�����־

    TAPIMatchSourceType            MatchSource;                        ///< �ɽ���Դ
    TAPISideType                OpenSide;                            ///< ���ַ���
    TAPIREAL64                    OpenPrice;                            ///< ���ּ۸�
    TAPIREAL64                    DeliveryPrice;                        ///< ����۸�
    TAPIUINT32                    DeliveryQty;                        ///< ������
    TAPIUINT32                    FrozenQty;                            ///< ������

    TAPISTR_20                    OpenNo;                                ///< ���ֳɽ���
    TAPISTR_10                    UpperNo;                            ///< ���ֱ��

    TAPISTR_10                    CommodityCurrencyGroupy;            ///< Ʒ�ֱ�����
    TAPISTR_10                    CommodityCurrency;                    ///< Ʒ�ֱ���
    TAPIREAL64                    PreSettlePrice;                        ///< ���ս����
    TAPIREAL64                    DeliveryProfit;                        ///< ����ӯ��

    TAPIREAL64                    AccountFrozenInitialMargin;            ///< �ͻ���ʼ���ᱣ֤��
    TAPIREAL64                    AccountFrozenMaintenanceMargin;        ///< �ͻ�ά�ֶ��ᱣ֤��
    TAPIREAL64                    UpperFrozenInitialMargin;            ///< ���ֳ�ʼ���ᱣ֤��
    TAPIREAL64                    UpperFrozenMaintenanceMargin;        ///< ����ά�ֶ��ᱣ֤��

    TAPISTR_10                    AccountFeeCurrencyGroup;            ///< �ͻ������ѱ�����
    TAPISTR_10                    AccountFeeCurrency;                    ///< �ͻ������ѱ���
    TAPIREAL64                    AccountDeliveryFee;                    ///< �ͻ�����������
    TAPISTR_10                    UpperFeeCurrencyGroup;              ///< ���������ѱ�����
    TAPISTR_10                    UpperFeeCurrency;                    ///< ���������ѱ���
    TAPIREAL64                    UpperDeliveryFee;                    ///< ���ֽ���������

    TAPIDeliveryModeType        DeliveryMode;                        ///< ������Ȩ��ʽ
    TAPISTR_20                    OperatorNo;                            ///< ����Ա
    TAPIDATETIME                OperateTime;                        ///< ����ʱ��
    TAPISTR_20                    SettleGroupNo;                        ///< �������
};

//! �ͻ��˻������Ѽ��������ѯ����ṹ��������ר�ã�
struct TapAPIAccountFeeRentQryReq
{
    TAPISTR_20                        AccountNo;        ///< �ͻ��ʽ��˺�
};
//! �ͻ��˻������Ѽ��������ѯӦ��ṹ��������ר�ã�
struct TapAPIAccountFeeRentQryRsp
{
    TAPISTR_20                        AccountNo;               ///< �ͻ��ʽ��˺�
    TAPISTR_10                        ExchangeNo;              ///< ����������
    TAPICommodityType                CommodityType;           ///< Ʒ������
    TAPISTR_10                        CommodityNo;             ///< Ʒ�ֱ��
    TAPIMatchSourceType                MatchSource;             ///< �ɽ���Դ
    TAPICalculateModeType            CalculateMode;
    TAPISTR_10                        CurrencyGroupNo;         ///< �������
    TAPISTR_10                        CurrencyNo;              ///< ���ֱ��
    TAPIREAL64                        OpenCloseFee;            ///< ��ƽ������
    TAPIREAL64                        CloseTodayFee;           ///< ƽ��������
    TAPISTR_10                      ContractNo;              ///< ��Լ
};

//! �ͻ��˻���֤����������ѯ�ṹ��������ר�ã�
struct TapAPIAccountMarginRentQryReq
{
    TAPISTR_20                        AccountNo;           ///< �ͻ��ʽ��˺�
    TAPISTR_10                        ExchangeNo;          ///< ����������
    TAPICommodityType                CommodityType;       ///< Ʒ������
    TAPISTR_10                        CommodityNo;         ///< Ʒ�ֱ��
    //TAPISTR_10                    ContractNo;          ///< ��ʱ�Ȳ����⿪�š�
};

//! �ͻ��˻���֤����������ѯӦ�𣨱�����ר�ã�
struct TapAPIAccountMarginRentQryRsp
{
    TAPISTR_20                        AccountNo;                ///< �ͻ��ʽ��˺�
    TAPISTR_10                        ExchangeNo;               ///< ����������
    TAPICommodityType                CommodityType;            ///< Ʒ������
    TAPISTR_10                        CommodityNo;              ///< Ʒ�ֱ��
    TAPISTR_10                        ContractNo;               ///< ��Լ����1
    TAPISTR_10                        StrikePrice;              ///< ִ�м�
    TAPICallOrPutFlagType            CallOrPutFlag;            ///< ���ǿ�����ʾ1
    TAPICalculateModeType            CalculateMode;            ///< ���㷽ʽ
    TAPISTR_10                        CurrencyGroupNo;          ///< �������
    TAPISTR_10                        CurrencyNo;               ///< ���ֱ��
    TAPIREAL64                        InitialMargin;            ///< ���ʼ��֤��
    TAPIREAL64                        MaintenanceMargin;        ///< ��ά�ֱ�֤��
    TAPIREAL64                        SellInitialMargin;        ///< ����ʼ��֤��
    TAPIREAL64                        SellMaintenanceMargin;    ///< ��ά�ֱ�֤��
    TAPIREAL64                        LockMargin;               ///< ���ֱ���
};

//! ������֤��Ϣ����Ӧ��ṹ
struct TapAPISecondInfo
{
    TAPISendTypeType               SendType;           ///< ��������
    TAPISTR_40                     SendAccount;        ///< �����˺�
};

//! ���������֤��Ȩ��Ӧ��
struct TapAPIVertificateCode
{
    TAPISecondSerialIDType SecondSerialID;                ///< ������֤��Ȩ�����
    TAPIINT32              Effective;                    ///< ������֤��Ȩ����Ч�ڣ��֣�
};

//! ������֤����ṹ
struct TapAPISecondCertificationReq
{
    TAPIPasswordType        PasswordType;              ///< ��������
    TAPISTR_10              VertificateCode;           ///< ������֤��
    TAPISecondLoginTypeType LoginType;                 ///< ������֤��¼����
};

//! ������֤Ӧ��ṹ
struct TapAPISecondCertificationRsp
{
   TAPIPasswordType        PasswordType;              ///< ��������
   TAPISTR_10              VertificateCode;           ///< ������֤��
   TAPISTR_10              SecondDate;                ///< ��һ�ζ�����֤����
};

//! ��¼�û��ֻ��豸��������ṹ
struct TapAPIMobileDeviceAddReq
{
    TAPISTR_20                    UserNo;                                    ///< �û����
    TAPISTR_30                  AppKey;
    TAPISTR_30                  AppID;
    TAPISTR_30                  MasterSecret;
    TAPISTR_50                  Cid;
    TAPISTR_10                  CompanyNo;
    TAPISTR_20                  CompanyAddressNo;
    TAPIDeviceTypeType          DeviceType;
};

//! ��¼�û��ֻ��豸����Ӧ��ṹ
typedef TapAPIMobileDeviceAddReq  TapAPIMobileDeviceAddRsp;

//! ������־��ѯ����ṹ
struct TapAPIManageInfoQryReq
{
    TAPIDATE                BeginDate;        ///< ��ʼ���ڣ�����
    TAPIDATE                EndDate;        ///< �������ڣ�����
};

//! ������־��ѯӦ��ṹ
struct TapAPIManageInfo
{
    TAPIUINT32             MsgID;                              ///< ���к�
    TAPISTR_50             SendFrom;                           ///< ������(�������ţ�����ʱΪ��)
    TAPICHAR               SendManageType;                       ///< ��������
    TAPISTR_20             AccountNo;                           ///< �ͻ��ʽ��˺�
    TAPISTR_200            SendAccount;                        ///< �����˺�(�ֻ��Ż�������)

    TAPISTR_200            Title;                              ///< ����
    TAPISTR_500            Content;                            ///< ����
    TAPISTR_500            Attachment;                         ///< ����
    TAPICHAR               SendStatus;                         ///< ����״̬
    TAPISTR_100            Remark;                             ///< ��ע(
    TAPISTR_100            GUID;                               ///< GUID

    TAPISTR_20             OperatorNo;                           ///< ������Ա���
    TAPIDATETIME           OperateTime;                           ///< ����ʱ��
};

//! ϵͳ������ѯ����ṹ
struct TapAPISystemParameterQryReq
{

};

//! ϵͳ������ѯӦ��ṹ
struct TapAPISystemParameterInfo
{
    TAPISTR_10                        ItemNo;                                ///< ��Ŀ���
    TAPISTR_10                        ExchangeNo;                            ///< ���������
    TAPISTR_10                        CommodityNo;                        ///< Ʒ�ֱ��
    TAPICommodityType                CommodityType;                        ///< Ʒ������
    TAPIINT32                        ItemValue;                            ///< ��Ŀֵ
    TAPISTR_20                        ItemValueStr;                        ///< ��Ŀֵ�ַ�������ֵ
    TAPIREAL64                        ItemValueDouble;                    ///< ��Ŀֵ����������ֵ
};

//! ��������ǰ�õ�ַ��Ϣ��ѯ����ṹ
struct TapAPITradeCenterFrontAddressQryReq
{
    TAPISTR_50                    FrontAddress;                        ///< ǰ�õ�ַ ��ղ�����
    TAPISTR_10                    FrontPort;                            ///< ǰ�ö˿� ��ղ�����
    TAPICHAR                    TradeCenter;                        ///< �������� ��ղ�����
    TAPICHAR                    IsSSL;                              ///< �Ƿ���ܶ˿�
};

//! ��������ǰ�õ�ַ��Ϣ��ѯӦ��ṹ
struct TapAPITradeCenterFrontAddressInfo
{
    TAPISTR_50                    FrontName;                            ///< ǰ������
    TAPISTR_50                    FrontAddress;                        ///< ǰ�õ�ַ
    TAPISTR_10                    FrontPort;                            ///< ǰ�ö˿�
    TAPICHAR                    TradeCenter;                        ///< ��������
    TAPICHAR                    IsEnable;                            ///< �Ƿ�����
    TAPICHAR                    IsSSL;                              ///< �Ƿ���ܶ˿�
};

//! �ͻ��ֻ�����ѯ����ṹ(������ר��)
struct TapAPIAccountStorageQryReq
{
    TAPISTR_20                        AccountNo;        ///< �ͻ��ʽ��ʺ�
};

//! �ͻ��ֻ������Ϣ(������ר��)
struct TapAPIAccountStorageInfo
{
    TAPISTR_20                        AccountNo;                ///< �ͻ��ʽ��ʺ�
    TAPISTR_10                        ExchangeNo;                  ///< ���������
    TAPICommodityType                CommodityType;              ///< Ʒ������
    TAPISTR_10                        CommodityNo;              ///< Ʒ�ֱ��
    TAPIREAL64                      StorageQty;                  ///< �����
};

//! �ͻ��ֻ���������ѯ����ṹ��ʹ�ÿͻ��ʽ��˺Ž�������(������ר��)
struct TapAPISpotLockQryReq
{
    TAPISTR_20                    StreamAccountNo;                ///< �ͻ��ʽ��ʺţ�����
    TAPISTR_20                    AccountNo;                        ///< �ͻ��ʽ��ʺ�
};

//! �ͻ��ֻ���������Ϣ
struct TapAPISpotLockInfo
{
    TAPISTR_20                    AccountNo;                        ///< �ͻ��ʽ��˺�

    TAPISTR_10                    ExchangeNo;                        ///< ����������
    TAPICommodityType            CommodityType;                    ///< Ʒ������
    TAPISTR_10                    CommodityNo;                    ///< Ʒ�ֱ��

    TAPIUINT32                    PositionQty;                    ///< �ֲ���
    TAPIUINT32                    LockQty;                        ///< ������
    TAPIUINT32                    CoveredQty;                        ///< �ѱ�����
    TAPIUINT32                    CanCoveredQty;                    ///< �ɱ�����
};

//! �ͻ�����ҵ��ί������(ETF��̨ר��)
struct TapAPISpecialOrderInsertReq
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��˺�
    TAPISpecialOrderTypeType    SpecialOrderType;                    ///< ����ҵ������
    TAPIOrderSourceType            OrderSource;                        ///< ί����Դ
    TAPISTR_50                  CombineNo;                          ///< ��ϱ���

    TAPISTR_50                  RefString;                          ///< �ַ����ο�ֵ

    TAPISTR_10                    ExchangeNo;                            ///< ����������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ��
    TAPISTR_10                    ContractNo;                            ///< ��Լ1
    TAPISTR_10                    StrikePrice;                        ///< ִ�м۸�1
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ſ���1
    TAPISTR_10                    ContractNo2;                        ///< ��Լ2
    TAPISTR_10                    StrikePrice2;                        ///< ִ�м۸�2
    TAPICallOrPutFlagType        CallOrPutFlag2;                        ///< ���ſ���2

    TAPIUINT32                    OrderQty;                            ///< ί������
    TAPISideType                OrderSide;                            ///< ��������
    TAPIHedgeFlagType            HedgeFlag;                            ///< Ͷ����ֵ

    TapAPISpecialOrderInsertReq()
    {
        memset(this, 0, sizeof(TapAPISpecialOrderInsertReq));
    }
};

//! �ͻ�����ҵ��ί��Ӧ��(ETF��̨ר��)
struct TapAPISpecialOrderInfo
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��˺�

    TAPICHAR                    ServerFlag;                            ///< ��������ʶ
    TAPISTR_20                    OrderNo;                            ///< ί�к�
    TAPISTR_50                  RefString;                          ///< �ַ����ο�ֵ

    TAPISpecialOrderTypeType    SpecialOrderType;                    ///< ����ҵ������
    TAPIOrderSourceType            OrderSource;                        ///< ί����Դ

    TAPICombineStrategyType     CombineStrategy;                    ///< ��ϲ��Դ���
    TAPISTR_50                  CombineNo;                            ///< ��ϱ���

    TAPIUINT32                    OrderQty;                            ///< ί������
    TAPISTR_10                    ExchangeNo;                            ///< ����������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ��

    TAPISTR_10                    ContractNo;                            ///< ��Լ1
    TAPISTR_10                    StrikePrice;                        ///< ִ�м۸�1
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ſ���1
    TAPISideType                OrderSide1;                            ///< ��������
    TAPIUINT32                    CombineQty1;                        ///< �������1
    TAPIHedgeFlagType            HedgeFlag1;                            ///< Ͷ����ֵ1

    TAPISTR_10                    ContractNo2;                        ///< ��Լ2
    TAPISTR_10                    StrikePrice2;                        ///< ִ�м۸�2
    TAPICallOrPutFlagType        CallOrPutFlag2;                        ///< ���ſ���2
    TAPISideType                OrderSide2;                            ///< ��������
    TAPIUINT32                    CombineQty2;                        ///< �������1
    TAPIHedgeFlagType            HedgeFlag2;                            ///< Ͷ����ֵ2

    TAPISTR_50                  LicenseNo;                            ///< �����Ȩ��

    TAPIUINT32                    OrderStreamID;                        ///< ί����ˮ��

    TAPISTR_10                    UpperNo;                            ///< ���ֺ�
    TAPISTR_10                    UpperChannelNo;                        ///< ����ͨ����
    TAPISTR_20                    OrderLocalNo;                        ///< ���غ�
    TAPISTR_50                    OrderSystemNo;                        ///< ϵͳ��
    TAPISTR_50                    OrderExchangeSystemNo;                ///< ������ϵͳ��

    TAPISTR_20                    OrderInsertUserNo;                    ///< �µ���
    TAPIDATETIME                OrderInsertTime;                    ///< �µ�ʱ��
    TAPIOrderStateType            OrderState;                            ///< ί��״̬

    TAPIUINT32                    ErrorCode;                            ///< ������Ϣ��
    TAPISTR_50                    ErrorText;                            ///< ������Ϣ

    TapAPISpecialOrderInfo()
    {
        memset(this, 0, sizeof(TapAPISpecialOrderInfo));
    }
};

//! �ͻ�����ҵ��ί�в�ѯ����ṹ
struct TapAPISpecialOrderQryReq
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��ʺţ���ղ��û��������пͻ���
    TAPIUINT32                    DataSeqID;                            ///< ������ʼ����
};

//! �ͻ���ϳֲֲ�ѯ����ṹ
struct TapAPICombinePositionQryReq
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��ʺţ���ղ��û��������пͻ���
    TAPIUINT32                    DataSeqID;                            ///< ������ʼ����
};

//! �ͻ���ϳֲ���Ϣ
struct TapAPICombinePositionInfo
{
    TAPISTR_20                    AccountNo;                            ///< �ͻ��ʽ��˺�

    TAPIUINT32                    PositionStreamId;                    ///< �ֲ�����
    TAPICHAR                    ServerFlag;                            ///< ��������ʶ
    TAPISTR_10                    UpperNo;                            ///< ���ֺ�

    TAPICombineStrategyType     CombineStrategy;                    ///< ��ϲ��Դ���
    TAPISTR_50                  CombineNo;                            ///< ��ϱ���
    TAPIUINT32                    PositionQty;                        ///< �ֲ���

    TAPISTR_10                    ExchangeNo;                            ///< ����������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ��

    TAPISTR_10                    ContractNo;                            ///< ��Լ1
    TAPISTR_10                    StrikePrice;                        ///< ִ�м۸�1
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ſ���1
    TAPISideType                OrderSide1;                            ///< ��������
    TAPIUINT32                    CombineQty1;                        ///< �������1
    TAPIHedgeFlagType            HedgeFlag1;                            ///< Ͷ����ֵ1

    TAPISTR_10                    ContractNo2;                        ///< ��Լ2
    TAPISTR_10                    StrikePrice2;                        ///< ִ�м۸�2
    TAPICallOrPutFlagType        CallOrPutFlag2;                        ///< ���ſ���2
    TAPISideType                OrderSide2;                            ///< ��������
    TAPIUINT32                    CombineQty2;                        ///< �������2
    TAPIHedgeFlagType            HedgeFlag2;                            ///< Ͷ����ֵ2

    TAPISTR_10                    CommodityCurrencyGroup;                ///< Ʒ�ֱ�����
    TAPISTR_10                    CommodityCurrency;                    ///< Ʒ�ֱ���

    TAPIREAL64                    AccountInitialMargin;                ///< �ͻ���ʼ��֤��
    TAPIREAL64                    AccountMaintenanceMargin;            ///< �ͻ�ά�ֱ�֤��
    TAPIREAL64                    UpperInitialMargin;                    ///< ���ֳ�ʼ��֤��
    TAPIREAL64                    UpperMaintenanceMargin;                ///< ����ά�ֱ�֤��

    TapAPICombinePositionInfo()
    {
        memset(this, 0, sizeof(TapAPICombinePositionInfo));
    }
};

//! ���׺�Լ������Ϣ
struct TapAPIContractQuoteInfo
{
    TAPISTR_10                    ExchangeNo;                            ///< ����������
    TAPICommodityType            CommodityType;                        ///< Ʒ������
    TAPISTR_10                    CommodityNo;                        ///< Ʒ�ֱ��

    TAPISTR_10                    ContractNo;                            ///< ��Լ1
    TAPISTR_10                    StrikePrice;                        ///< ִ�м۸�1
    TAPICallOrPutFlagType        CallOrPutFlag;                        ///< ���ſ���1
    
    TAPIREAL64                    LastPrice;                          ///< ���¼�
    TAPIREAL64                    PreSettlePrice;                     ///< ������
    TAPIREAL64                    PreClosingPrice;                    ///< �����̼�
    TAPIREAL64                    LimitUpPrice;                       ///< ��ͣ��
    TAPIREAL64                    LimitDownPrice;                     ///< ��ͣ��
};

//! ���õ�¼��ַ��Ϣ
struct TapAPIBackUpAddress
{
    TAPISTR_40                    LoginIP;                            ///< ��¼IP
    TAPIUINT32                    LoginPort;                            ///< ��¼�˿�
};

//! �����֤��Ϣ
struct TapAPIVerifyIdentity
{
    TAPISTR_20                    UserNo;                                    ///< �û����
    TAPICertificateType         CertificateType;                        ///< ֤������
    TAPISTR_50                  CertificateNo;                            ///< ֤������
    TAPISTR_40                  EMail;                                    ///< ���������˺�
    TAPISTR_20                  PhoneNo;                                ///< �ֻ���
};

//! �û������豸��ѯ����
struct TapAPITrustDeviceQryReq
{
};

//! �û������豸��Ϣ
struct TapAPITrustDeviceInfo
{
    TAPISTR_20                    UserNo;                                ///< �û����
    TAPISTR_50                    LicenseNo;                            ///< �����Ȩ��
    TAPISTR_50                    Mac;                                ///< Mac��ַ
    TAPISTR_50                    DeviceName;                            ///< �豸����   
};

//! �û������豸��������ṹ��
typedef TapAPITrustDeviceInfo TapAPITrustDeviceAddReq;

//! �û������豸����Ӧ��ṹ��
typedef TapAPITrustDeviceAddReq TapAPITrustDeviceAddRsp;

//! �û������豸ɾ������ṹ��
struct TapAPITrustDeviceDelReq
{
    TAPISTR_20                    UserNo;                                ///< �û����
    TAPISTR_50                    LicenseNo;                            ///< �����Ȩ��
    TAPISTR_50                    Mac;                                ///< Mac��ַ
};

//! �û������豸ɾ��Ӧ��ṹ��
typedef TapAPITrustDeviceDelReq TapAPITrustDeviceDelRsp;

//! ������С�䶯��
struct TapAPIStepTickSize
{
    TAPISTR_10                    ExchangeNo;                            ///< ����������
    TAPIREAL64                    BeginPrice;                         ///< ��ʼ��λ
    TAPIREAL64                    EndPrice;                           ///< ������λ
    TAPIREAL64                    TickSize;                           ///< ��С�䶯��
};

//! ��̨�����ļ���ѯ����ṹ
struct TapAPIManagerConfigFileQryReq
{
    TAPISTR_50                  FileName;                           ///< �ļ���
    TAPISTR_50                  FileDirectory;                      ///< �ļ�����Ŀ¼������ļ���Ϊ���򷵻�ȫ����Ŀ¼���ļ�
};

//! ��̨�����ļ���ѯӦ��ṹ
struct TapAPIManagerConfigFileQryRsp
{
    TapAPIManagerConfigFileQryReq Reqdata;                          ///< ��̨�����ļ���ѯ��������
    TAPIINT32                      ManagerConfigFileLen;             ///< ��̨�����˵��ļ�����
    TAPICHAR                      ManagerConfigFileText[1];         ///< �䳤��̨�������ݣ�������BillLenָ��
};

#pragma pack(pop)

}

#endif //ES_TRADE_API_STRUCT_H
