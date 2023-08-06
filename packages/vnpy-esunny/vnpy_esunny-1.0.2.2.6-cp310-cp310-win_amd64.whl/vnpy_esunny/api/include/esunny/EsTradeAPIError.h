/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/*
 * File:   EsTradeAPIError.h
 * Author: guoxg
 *
 * Created on 2018��5��24��, ����2:50
 */

#ifndef ESTRADEAPIERROR_H
#define ESTRADEAPIERROR_H

namespace EsTradeAPI
{

	//=============================================================================
	/**
	 *	\addtogroup G_ERR_INNER_API		EsAPI�ڲ����صĴ����붨��
	 *	@{
	 */
	 //=============================================================================
	 //! �ɹ�
	const int TAPIERROR_SUCCEED = 0;
	//! ���ӷ���ʧ��
	const int TAPIERROR_ConnectFail = -1;
	//! ��·��֤ʧ��
	const int TAPIERROR_LinkAuthFail = -2;
	//! ������ַ������
	const int TAPIERROR_HostUnavailable = -3;
	//! �������ݴ���
	const int TAPIERROR_SendDataError = -4;
	//! ���Ա�Ų��Ϸ�
	const int TAPIERROR_TestIDError = -5;
	//! û׼���ò�������
	const int TAPIERROR_NotReadyTestNetwork = -6;
	//! ��ǰ������Ի�û����
	const int TAPIERROR_CurTestNotOver = -7;
	//! û�ÿ��õĽ���ǰ��
	const int TAPIERROR_NOFrontAvailable = -8;
	//! ��־�ļ�·��������
	const int TAPIERROR_DataPathAvaiable = -9;
	//! �ظ���¼
	const int TAPIERROR_RepeatLogin = -10;
	//! �ڲ�����
	const int TAPIERROR_InnerError = -11;
	//! ��һ������û�н���
	const int TAPIERROR_LastReqNotFinish = -12;
	//! ��������Ƿ�
	const int TAPIERROR_InputValueError = -13;
	//! ��Ȩ�벻�Ϸ�
	const int TAPIERROR_AuthCode_Invalid = -14;
	//! ��Ȩ�볬��
	const int TAPIERROR_AuthCode_Expired = -15;
	//! ��Ȩ�����Ͳ�ƥ��
	const int TAPIERROR_AuthCode_TypeNotMatch = -16;
	//! API��û��׼����
	const int TAPIERROR_API_NotReady = -17;
	//! UDP�˿ڼ���ʧ��
	const int TAPIERROR_UDP_LISTEN_FAILED = -18;
	//! UDP���ڼ���
	const int TAPIERROR_UDP_LISTENING = -19;
	//! �ӿ�δʵ��
	const int TAPIERROR_NotImplemented = -20;
	//! ֻ�������һ��
	const int TAPIERROR_CallOneTimeOnly = -21;
	//! ����Ƶ��̫��
	const int TAPIERROR_Frequently = -22;
	//! �û�����ظ�
	const int TAPIERROR_UserNoDuplicate = -23;
	//! �û���Ŵ���
	const int TAPIERROR_UserNoError = -24;
	//! û������Ҫ��ѯ������
	const int TAPIERROR_HaveNoData = -25;
	//! �û��Ѿ���������Ҫ�ٴ�����
	const int TAPIERROR_UserReady = -26;
	//! ��֧�ֵĲ�������
	const int TAPIERROR_NotSupportType = -27;
	//! ��ǰ�û���Ӧ��ϵͳ�ݲ�֧�ֵĹ���
	const int TAPIERROR_NotSupportFunction = -28;
	//! �û���¼��Ϣ������
	const int TAPIERROR_LoginInfoIncompletion = -29;
	//! ���м��û����������ϱ���¼��Ϣ
	const int TAPIERROR_NotAllowSubmit = -30;
	//! �����²�API��̬��ʧ��
	const int TAPIERROR_LoadDll = -31;
	//! ��־�ļ��Ѿ���
	const int TAPIERROR_LogFileReady = -32;
	//! ����־�ļ�����
	const int TAPIERROR_LogFile_OpenError = -33;
	//! ����TCPClientʧ��
	const int TAPIERROR_CreateTcpClient_Error = -34;
    //! �����ϵͳ����
    const int TAPIERROR_SystemType_Error = -35;
	//! ��¼�ɹ����������
	const int TAPIERROR_NotAllowAfterLogin = -36;
	//! ��֤����Ч���ڲ�����ڶ�������
	const int TAPIERROR_NotAllowRequestAgain = -37;
    //! ��¼��Ȩ�벻����Ϊ��
    const int TAPIERROR_NoNULLAuthCode = -38;
    //! �û�������Ϊ��
    const int TAPIERROR_UserNoNULL = -39;
    //! �����û��͵�¼�û�����ͬ
    const int TAPIERROR_UserNoSame = -40;
    //! ���û���û�и�ί��
    const int TAPIERROR_UserNoHasOrder = -41;
    //! ���ñ��õ�ַ�ظ�
    const int TAPIERROR_BackUpAddressRepeat = -42;
    //! ����������������
    const int TAPIERROR_PasswordType = -43;
    //! �������ĵ�¼����
    const int TAPIERROR_LoginType = -44;
    //! ��������ǰ��Ҫ��ͨ�������֤
    const int TAPIERROR_Identity = -45;
    //! ��������ǰ��Ҫ��ͨ����֤����֤
    const int TAPIERROR_VertificateCode = -46;
    //! ֻ�������û�֧��
    const int TAPIERROR_OnlyEstarSupport = -47;
    //! ��̨��֧�ָ�Э��
    const int TAPIERROR_ProtocolSupport = -48;
    //! ί�м۸񾫶Ȳ���
    const int TAPIERROR_OrderPricePrecision = -49;
    //! ί�м���С�䶯�۲���
    const int TAPIERROR_OrderPriceInvalid = -50;
	/** @}*/


	//=============================================================================
	/**
	 *	\addtogroup G_ERR_INPUT_CHECK		�������������
	 *	@{
	 */
	 //=============================================================================
	 //! ��������ΪNULL
	const int TAPIERROR_INPUTERROR_NULL = -10000;
	//! ��������:TAPIYNFLAG
	const int TAPIERROR_INPUTERROR_TAPIYNFLAG = -10001;
	//! ��������:TAPILOGLEVEL
	const int TAPIERROR_INPUTERROR_TAPILOGLEVEL = -10002;
	//! ��������:TAPICommodityType
	const int TAPIERROR_INPUTERROR_TAPICommodityType = -10003;
	//! ��������:TAPICallOrPutFlagType
	const int TAPIERROR_INPUTERROR_TAPICallOrPutFlagType = -10004;
	//! ��������:TAPISystemTypeType
	const int TAPIERROR_INPUTERROR_TAPISystemTypeType = -10005;
	//! ��������:TAPILoginTypeType
	const int TAPIERROR_INPUTERROR_TAPILoginTypeType = -10006;
	//! ��������:TAPIAccountType
	const int TAPIERROR_INPUTERROR_TAPIAccountType = -12001;
	//! ��������:TAPIAccountState
	const int TAPIERROR_INPUTERROR_TAPIAccountState = -12003;
	//! ��������:TAPIAccountFamilyType
	const int TAPIERROR_INPUTERROR_TAPIAccountFamilyType = -12004;
	//! ��������:TAPIOrderTypeType
	const int TAPIERROR_INPUTERROR_TAPIOrderTypeType = -12005;
	//! ��������:TAPIOrderSourceType
	const int TAPIERROR_INPUTERROR_TAPIOrderSourceType = -12006;
	//! ��������:TAPITimeInForceType
	const int TAPIERROR_INPUTERROR_TAPITimeInForceType = -12007;
	//! ��������:TAPISideType
	const int TAPIERROR_INPUTERROR_TAPISideType = -12008;
	//! ��������:TAPIPositionEffectType
	const int TAPIERROR_INPUTERROR_TAPIPositionEffectType = -12009;
	//! ��������:TAPIHedgeFlagType
	const int TAPIERROR_INPUTERROR_TAPIHedgeFlagType = -12010;
	//! ��������:TAPIOrderStateType
	const int TAPIERROR_INPUTERROR_TAPIOrderStateType = -12011;
	//! ��������:TAPICalculateModeType
	const int TAPIERROR_INPUTERROR_TAPICalculateModeType = -12012;
	//! ��������:TAPIMatchSourceType
	const int TAPIERROR_INPUTERROR_TAPIMatchSourceType = -12013;
	//! ��������:TAPIOpenCloseModeType
	const int TAPIERROR_INPUTERROR_TAPIOpenCloseModeType = -12014;
	//! ��������:TAPIFutureAlgType
	const int TAPIERROR_INPUTERROR_TAPIFutureAlgType = -12015;
	//! ��������:TAPIOptionAlgType
	const int TAPIERROR_INPUTERROR_TAPIOptionAlgType = -12016;
	//! ��������:TAPIBankAccountLWFlagType
	const int TAPIERROR_INPUTERROR_TAPIBankAccountLWFlagType = -12017;
	//! ��������:TAPIMarginCalculateModeType
	const int TAPIERROR_INPUTERROR_TAPIMarginCalculateModeType = -12021;
	//! ��������:TAPIOptionMarginCalculateModeType
	const int TAPIERROR_INPUTERROR_TAPIOptionMarginCalculateModeType = -12022;
	//! ��������:TAPICmbDirectType
	const int TAPIERROR_INPUTERROR_TAPICmbDirectType = -12023;
	//! ��������:TAPIDeliveryModeType
	const int TAPIERROR_INPUTERROR_TAPIDeliveryModeType = -12024;
	//! ��������:TAPIContractTypeType
	const int TAPIERROR_INPUTERROR_TAPIContractTypeType = -12025;
	//! ��������:TAPITacticsTypeType
	const int TAPIERROR_INPUTERROR_TAPITacticsTypeType = -12035;
	//! ��������:TAPIORDERACT
	const int TAPIERROR_INPUTERROR_TAPIORDERACT = -12036;
	//! ��������:TAPITriggerConditionType
	const int TAPIERROR_INPUTERROR_TAPITriggerConditionType = -12041;
	//! ��������:TAPITriggerPriceTypeType
	const int TAPIERROR_INPUTERROR_TAPITriggerPriceTypeType = -12042;
	//! ��������:TAPITradingStateType
	const int TAPIERROR_INPUTERROR_TAPITradingStateType = -12043;
	//! ��������:TAPIMarketLevelType
	const int TAPIERROR_INPUTERROR_TAPIMarketLevelType = -12044;
	//! ��������:TAPIOrderQryTypeType
	const int TAPIERROR_INPUTERROR_TAPIOrderQryTypeType = -12045;
	//! �������ģ�TapAPICommodity
	const int TAPIERROR_INPUTERROR_TAPICommodity = -12046;
	//! �������ģ�TAPIContract
	const int TAPIERROR_INPUTERROR_TAPIContract = -12047;
	//! ��������:TAPIOrderPriceTypeType
	const int TAPIERROR_INPUTERROR_TAPIOrderPriceTypeType = -12048;
	//! ��������:TAPIExpireTime
	const int TAPIERROR_INPUTERROR_TAPIExpireTime = -12049;
	//! �������Ķ�����֤��Ϣ
	const int TAPIERROR_INPUTERROR_VertificateCode = -12050;
	//! �������: AddOneIsValid
	const int TAPIERROR_INPUTERROR_TAPIAddOneIsValid = -12051;
    //! �������: SpecialOrderType
	const int TAPIERROR_INPUTERROR_TAPISpecialOrderTypeType = -12052;
    //! �������: ClientID��ClientID���������ַ�
    const int TAPIERROR_INPUTERROR_TAPIClientID = -12053;
    //! �������: ISModifyPassword
    const int TAPIERROR_INPUTERROR_TAPIForceModifyPasswordType = -12054;
    //! �������: CertificateType
    const int TAPIERROR_INPUTERROR_TAPICertificateType = -12055;
    //! �������: SendType
    const int TAPIERROR_INPUTERROR_TAPISendTypeType = -12056;
    //! �������: PasswordType
    const int TAPIERROR_INPUTERROR_TAPIPasswordType = -12057;
    //! �������: SecondLoginType
    const int TAPIERROR_INPUTERROR_TAPISecondLoginTypeType = -12058;

	/** @}*/

	//=============================================================================
	/**
	 *	\addtogroup G_ERR_DISCONNECT_REASON	����Ͽ�������붨��
	 *	@{
	 */
	 //=============================================================================
	 //! �����Ͽ�
	const int TAPIERROR_DISCONNECT_CLOSE_INIT = 1;
	//! �����Ͽ�
	const int TAPIERROR_DISCONNECT_CLOSE_PASS = 2;
	//! ������
	const int TAPIERROR_DISCONNECT_READ_ERROR = 3;
	//! д����
	const int TAPIERROR_DISCONNECT_WRITE_ERROR = 4;
	//! ��������
	const int TAPIERROR_DISCONNECT_BUF_FULL = 5;
	//! �첽��������
	const int TAPIERROR_DISCONNECT_IOCP_ERROR = 6;
	//! �������ݴ���
	const int TAPIERROR_DISCONNECT_PARSE_ERROR = 7;
	//! ���ӳ�ʱ
	const int TAPIERROR_DISCONNECT_CONNECT_TIMEOUT = 8;
	//! ��ʼ��ʧ��
	const int TAPIERROR_DISCONNECT_INIT_ERROR = 9;
	//! �Ѿ�����
	const int TAPIERROR_DISCONNECT_HAS_CONNECTED = 10;
	//! �����߳��ѽ���
	const int TAPIERROR_DISCONNECT_HAS_EXIT = 11;
	//! �������ڽ��У����Ժ�����
	const int TAPIERROR_DISCONNECT_TRY_LATER = 12;
	//! �������ʧ��
	const int TAPIERROR_DISCONNECT_HEARTBEAT_FAILED = 13;
	//! Socket�������
	const int TAPIERROR_DISCONNECT_SOCKETSELECT_ERROR = 14;
	//! �����ǳ�
	const int TAPIERROR_DISCONNECT_LOGOUT = 15;
	/** @}*/

	//=============================================================================
	/**
	 *	\addtogroup G_ERR_LOGIN	��½���̷��صĴ�����붨��
	 *	@{
	 */
	 //=============================================================================
	//! ��¼����ִ�д���
	const int TAPIERROR_LOGIN = 210001;
	//! ��¼�û�������
	const int TAPIERROR_LOGIN_USER = 210002;
	//! ��Ҫ���ж�̬��֤
	const int TAPIERROR_LOGIN_DDA = 210003;
	//! ��¼�û�δ��Ȩ
	const int TAPIERROR_LOGIN_LICENSE = 210004;
	//! ��¼ģ�鲻��ȷ
	const int TAPIERROR_LOGIN_MODULE = 210005;
	//! ��Ҫǿ���޸�����
	const int TAPIERROR_LOGIN_FORCE = 210006;
	//! ��¼״̬��ֹ��½
	const int TAPIERROR_LOGIN_STATE = 210007;
	//! ��¼���벻��ȷ
	const int TAPIERROR_LOGIN_PASS = 210008;
	//! û�и�ģ���¼Ȩ��
	const int TAPIERROR_LOGIN_RIGHT = 210009;
	//! ��¼��������
	const int TAPIERROR_LOGIN_COUNT = 210010;
	//! ��¼�û����ڷ�������ʶ�¿ɵ�¼�û��б���
	const int TAPIERROR_LOGIN_NOTIN_SERVERFLAGUSRES = 210011;
	//! ��½�û���������֤����
	const int TAPIERROR_LOGIN_USER_EXPIRED = 210012;
	//! ��½�û��������ͻ�
	const int TAPIERROR_LOGIN_NO_ACCOUNT = 210013;
	//! ��¼�û������ʺ�����Ȩ��δ��������ͨ���
	const int TAPIERROR_LOGIN_NO_JGT = 210014;
	//! ��¼�û��������������ޣ���ֹ��½
	const int TAPIERROR_LOGIN_ERROR_TIMES = 210015;
	//! ��¼�û���Ȩ���ʹ���
	const int TAPIERROR_LOGIN_SECONDCERTIFICATION = 210016;
	//! ��¼�û���Ȩ���ڻ����մ���
	const int TAPIERROR_LOGIN_ERROR_AUTHEXPIRED = 210017;
	//! ��¼�û����볬����Ч����
	const int TAPIERROR_LOGIN_ERROR_PASSWDEXPIRED = 210018;
	//! ��¼�û�δ��Ȩ�ĵ�¼IP��MAC
	const int TAPIERROR_LOGIN_ERROR_USERTRUST = 210019;
    //! 8.2�ͻ��˽�ֹ��¼������8.3
    const int TAPIERROR_LOGIN_ERROR_CLIENTVERSION = 210020;
    //! �û���Ȩ��Ϣ����
    const int TAPIERROR_LOGIN_ERROR_AUTHCODEINFO = 210021;

	//! ��¼����ִ�д���
	const int TAPIERROR_ILOGIN = 110001;
	//! ��¼�û�������
	const int TAPIERROR_ILOGIN_USER = 110002;
	//! ��Ҫ���ж�̬��֤
	const int TAPIERROR_ILOGIN_DDA = 110003;
	//! ��¼�û�δ��Ȩ
	const int TAPIERROR_ILOGIN_LICENSE = 110004;
	//! ��¼ģ�鲻��ȷ
	const int TAPIERROR_ILOGIN_MODULE = 110005;
	//! ��Ҫǿ���޸�����
	const int TAPIERROR_ILOGIN_FORCE = 110006;
	//! ��¼״̬��ֹ��½
	const int TAPIERROR_ILOGIN_STATE = 110007;
	//! ��¼���벻��ȷ
	const int TAPIERROR_ILOGIN_PASS = 110008;
	//! û�и�ģ���¼Ȩ��
	const int TAPIERROR_ILOGIN_RIGHT = 110009;
	//! ��¼��������
	const int TAPIERROR_ILOGIN_COUNT = 110010;
	//! ��¼�û����ڷ�������ʶ�¿ɵ�¼�û��б���
	const int TAPIERROR_ILOGIN_NOTIN_SERVERFLAGUSRES = 110011;
	//! ��¼�û��ѱ�����
	const int TAPIERROR_ILOGIN_FREEZE = 110012;
	//! ��������û�����
	const int TAPIERROR_ILOGIN_TOFREEZE = 110013;
	//! �ͻ�״̬�������¼
	const int TAPIERROR_ILOGIN_ACCOUNTSTATE = 110014;
	//! ��Ҫ���ж�����֤
	const int TAPIERROR_ILOGIN_SECCERTIFI = 110015;
	//! δ�󶨶�����֤��Ϣ
	const int TAPIERROR_ILOGIN_NOSECONDSET = 110016;
	//! �������εļ������¼
	const int TAPIERROR_ILOGIN_NOTURSTHOST = 110017;
	//! �����ά��ʧ��
	const int TAPIERROR_ILOGIN_GETQRCODE = 110018;
	//! �Ǳ��������Ŀͻ�
	const int TAPIERROR_ILOGIN_NOTINTRADECENTER = 110019;
	//! �汾�ͺ�̨�汾����һ��
	const int TAPIERROR_ILOGIN_INCONSISTENT = 110020;
	//! �ͻ�������������ǰ�õ�ַδ����
	const int TAPIERROR_ILOGIN_NOCENTERFRONTADDRESS = 110021;
	//! ��������˺����͵�¼
	const int TAPIERROR_ILOGIN_PROHIBITACCOUNTTYPE = 110022;
    //! ��Ҫ��Ϣ�ɼ�-ֱ��
    const int TAPIERROR_ILOGIN_GATHERINFO_DIRECT = 110023;
    //! ��Ҫ��Ϣ�ɼ�-�м�
    const int TAPIERROR_ILOGIN_GATHERINFO_RELAY = 110024;
    //! ������������
    const int TAPIERROR_ILOGIN_RESET_PASSWORD = 110025;
    //! �����������Ӵ�������
    const int TAPIERROR_ILOGIN_RESET_PASSWORD_EXCEEDED = 110026;
    //! ��֧�ֲ���Ա��������
    const int TAPIERROR_ILOGIN_OPERATOR_UNALLOWED_RESET = 110027;
    //! ������������
    const int TAPIERROR_ILOGIN_RESET_PASSWORD_FROZEN = 110028;
    //! �����֤ʧ��
    const int TAPIERROR_ILOGIN_VERIFYIDENTITY_FAILED = 110029;
    //! �����֤��������
    const int TAPIERROR_ILOGIN_VERIFYIDENTITY_EXCEED = 110030;
    //! ��Ȩ�ѵ���
    const int TAPIERROR_ILOGIN_LICENSE_EXPIRED = 110031;
    //! ��������������-û�����÷��ͷ�ʽ
    const int TAPIERROR_ILOGIN_PROHIBITRESETPASSWORD = 110032;
    //! ������״̬�ⶳ
    const int TAPIERROR_ILOGIN_UNFREEZE	= 110033;
    //! ����״̬�ⶳ��������������
    const int TAPIERROR_ILOGIN_UNFREEZE_EXCEEDED = 110034;
    //! ������ⶳ-û�����÷��ͷ�ʽ
    const int TAPIERROR_ILOGIN_PROHIBIT_UNFREEZE = 110035;
    //! ����Ҫ�ⶳ-��¼δ����
    const int TAPIERROR_ILOGIN_NONEED_UNFREEZE = 110036;

	/** @}*/

	//=============================================================================
	/**
	 *	\addtogroup G_ERR_MANAGE ����ҵ�����ش�����
	 *	@{
	 */
	 //==============================================================================
	//! ��¼�û���Ϣ��ѯʧ��
	const int TAPIERROR_USERINFO_QRY = 210101;
	//! ��¼�û�����Ȩ�޲�ѯʧ��
	const int TAPIERROR_USERRIGHT_QRY = 210901;
	//! ��¼�û���������Ȩ�޲�ѯʧ��
	const int TAPIERROR_USERALLRIGHT_QRY = 211001;
	//! ��¼�û����������ʽ��˺Ų�ѯʧ��
	const int TAPIERROR_USERALLACCOUNT_QRY = 211501;
	//! ��¼�û������޸�ʧ��
	const int TAPIERROR_USERPASSWORD_MOD = 211701;
	//! ��¼�û������޸�ʧ��,ԭʼ�������
	const int TAPIERROR_USERPASSWORD_MOD_SOURCE = 211702;
	//! ��¼�û������޸�ʧ��,������ǰn��������ͬ
	const int TAPIERROR_USERPASSWORD_MOD_SAME = 211703;
	//! �����벻�������븴�Ӷ�Ҫ��
	const int TAPIERROR_USERPASSWORD_MOD_COMPLEXITY = 211704;
	//! ���ױ��ֲ�ѯʧ��
	const int TAPIERROR_TCURRENCYINFO_QRY = 220102;
	//! �ʽ��˺���Ϣ��ѯʧ��
	const int TAPIERROR_ACCOUNTINFO_QRY = 220201;
	//! ��������Ϣ��ѯʧ��
	const int TAPIERROR_EXCHANGEINFO_QRY = 220601;
	//! �ͻ����ױ����ѯʧ��
	const int TAPIERROR_TRADENO_QRY = 220701;
	//!����ͨ����Ϣ��ѯʧ��
	const int TAPIERROR_UPPERCHANNEL_QRY = 221401;
	//! Ʒ����Ϣ��ѯʧ��
	const int TAPIERROR_COMMODITYINFO_QRY = 222001;
	//! ��Լ��Ϣ��ѯʧ��
	const int TAPIERROR_CONTRACTINFO_QRY = 222801;
	//! ������Ȩ��Ĳ�ѯʧ��
	const int TAPIERROR_SPECIALOPTIONFUTURE_QRY = 222901;
	//! �û��µ�Ƶ�ʲ�ѯʧ��
	const int TAPIERROR_USER_ORDER_FREQUENCE_QRY = 228901;
	//! �ͻ����������Ѳ�ѯʧ��
	const int TAPIERROR_ACCOUNTFEE_PARAMETER_QRY = 229431;
	//! �ͻ����ձ�֤���ѯʧ��
	const int TAPIERROR_ACCOUNTMARGIN_PARAMETER_QRY = 229432;
    //! �ύ��Ϣ�û���Ȩ���ʹ���
    const int TAPIERROR_USERSUBMITAUTHTYPE_ERROR = 229591;
    //! �û��ɼ��ն�����Ϊ��
    const int TAPIERROR_USERSUBMITINFO_EMPTY = 229592;
    //! �û���Կ�汾����
    const int TAPIERROR_USERAUTHKEYVERSION_ERROR = 229593;
    //! �û��ɼ���Ϣ��ȫ��Ȩ�޲���
    const int TAPIERROR_USERSUBMITINFO_PARTY = 229594;
    //! �û��ɼ���Ϣ���ò�����Կ����
    const int TAPIERROR_USERSUBMITINFO_TESTKEY = 229595;
    //! �û��ɼ���Ϣ�û�������
    const int TAPIERROR_USERSUBMITINFO_USERNO = 229596;
	//! ������Ϣ���ʹ���
	const int TAPIERROR_TRADEMESSAGE_SEND = 242301;
	//! ������Ϣ��ѯ����
	const int TAPIERROR_TRADEMESSAGE_QRY = 242302;
	//! ������Ϣ����֪ͨ����
	const int TAPIERROR_TRADEMESSAGE_NOTICE = 242303;
	//! ������Ϣ��Чʱ���ڲ�ѯ����
	const int TAPIERROR_TRADEMESSAGEINVALIDTIME_QRY = 242304;


	//! ���ݿ�����ʧ��
	const int TAPIERROR_CONN_DATABASE = 111000;
	//! ���ݿ����ʧ��
	const int TAPIERROR_OPER_DATABASE = 111001;
	//! ������һ�Զ�
	const int TAPIERROR_NEED_ONETOONE = 111002;
	//! ɾ��ʧ��-���ڹ�����Ϣ
	const int TAPIERROR_EXIST_RELATEINFO = 111003;
	//! ɾ������ʧ��-�������������ڲ���Ա������
	const int TAPIERROR_EXIST_RELATEINFOOFGROUP = 111004;
	//! ������Գ�������Ա����
	const int TAPIERROR_FORBIDDEN_SUPER = 111005;
	//! ���״̬�������޸�
	const int TAPIERROR_CHECK_FAILED = 111006;
	//! ����������ظ�3.0�ⲿƷ�ֱ��
	const int TAPIERROR_EXIST_OUTSIDECOMMODITYNO = 111007;
	//! �ͻ����㵥������
	const int TAPIERROR_NOTEXIST_BILL = 111008;
	//! ���������Ӵ������˺�
	const int TAPIERROR_LOGIN_PROHIBITADDACCOUNTTYPE = 111009;
	//! �˺����Ͳ�����Ϊ��
	const int TAPIERROR_ACCOUNTINFO_NOTEXPTY = 111010;
	//! ���˺Ų�����Ϊ��
	const int TAPIERROR_ACCOUNTINFO_SuperiorNOTEMPTY = 111011;
    //! ���������豸����������
    const int TAPIERROR_USERTRUSTDEVICE_ADDLIMITE = 111012;
    //! �Ƿ�ӳ��
    const int TAPIERROR_UPPERACCOUNTMAPPING_NOTALLOW = 111013;

	//! ��¼�û������޸�ʧ��-ԭʼ�������
	const int TAPIERROR_IUSERPASSWORD_MOD_SOURCE = 112001;
	//! ��¼�û������޸�ʧ��-������ǰn��������ͬ
	const int TAPIERROR_IUSERPASSWORD_MOD_SAME = 112002;
	//! ��¼�û������޸�ʧ��-�����벻�������븴�Ӷ�Ҫ��
	const int TAPIERROR_IUSERPASSWORD_MOD_COMPLEXITY = 112003;
    
    //! һ��������ֻ������һ������
    const int TAPIERROR_CURRENCY_ONLY_ONEBASE = 113001;
    //! ����ֻ������Ԫ��۱�
    const int TAPIERROR_CURRENCY_ONLY_USDHKD = 113002;

	//! ������֤ʧ��
	const int TAPIERROR_SECONDCERTIFICATION_FAIL = 114001;
	//! ������֤��ʱ
	const int TAPIERROR_SECONDCERTIFICATION_TIMEOVER = 114002;
	//! ������֤����������ޣ����µ�¼
	const int TAPIERROR_SECONDCERTIFICATION_RELOGIN = 114003;
	//! ������֤����������ޣ��û�����
	const int TAPIERROR_SECONDCERTIFICATION_FREEZE = 114004;
    
    //! �ڻ���˾��������������
    const int TAPIERROR_AUTOSWAP_NOTALLOWED = 115001;
    //! �ڻ���˾�����ڸ�ʱ�λ���
    const int TAPIERROR_AUTOSWAP_TIMENOTALLOWED = 115002;
    //! �������ʶ��
    const int TAPIERROR_AUTOSWAP_SINGLEQUOTA = 115003;
    //! �������մ���
    const int TAPIERROR_AUTOSWAP_SINGLEDAY = 115004;
    //! �������ն��
    const int TAPIERROR_AUTOSWAP_ONEDAYQUOTA = 115005;
    //! ������˾���ն��
    const int TAPIERROR_AUTOSWAP_COMPANYONEDAYQUOTA = 115006;
    
    //! ��Ѻ����������Ѻ����
    const int TAPIERROR_PLEDGE_OUTOFRANGE = 116001;

	//! ��Կδ�ҵ�
	const int TAPIERROR_GATHERINFO_NO_AUTHKEY = 117001;
	//! ��֤ʧ��
	const int TAPIERROR_GATHERINFO_AUTH_FAILED = 117002;

	/** @}*/

	//=============================================================================
	/**
	 *	\addtogroup G_ERR_TRADE ����ҵ�����ش�����
	 *	@{
	 */
	 //==============================================================================
	 //! �ʽ��˺Ų�����
	const int TAPIERROR_ORDERINSERT_ACCOUNT = 260001;
	//! �ʽ��˺�״̬����ȷ
	const int TAPIERROR_ORDERINSERT_ACCOUNT_STATE = 260002;
	//! �ʽ��˺���ί�з�����Ȩ��
	const int TAPIERROR_ORDERINSERT_SIDE_TRADE = 260003;
	//! �ʽ��˺�����Ȩ����Ȩ��
	const int TAPIERROR_ORDERINSERT_OPTIONS_TRADE = 260004;
	//! �ʽ��˺���Ʒ�ֽ���Ȩ��
	const int TAPIERROR_ORDERINSERT_COMMODITY_TRADE = 260005;
	//! �ʽ��˺��޿���Ȩ��
	const int TAPIERROR_ORDERINSERT_OPEN_RIGHT = 260006;
	//! �ʽ��˺ŷ������ʧ��
	const int TAPIERROR_ORDERINSERT_RISK_CHECK = 260007;
	//! �µ���Ч�ĺ�Լ
	const int TAPIERROR_ORDERINSERT_CONTRACT = 260011;
	//! �µ���Լ�޽���·��
	const int TAPIERROR_ORDERINSERT_TRADEROUTE = 260021;
	//! �ֲ��������������
	const int TAPIERROR_ORDERINSERT_POSITIONMAX = 260022;
	//! ��ֹ����
	const int TAPIERROR_ORDER_NOTRADE = 260023;
	//! ֻ��ƽ��
	const int TAPIERROR_ORDER_CLOSE = 260024;
	//! �µ��ʽ���
	const int TAPIERROR_ORDERINSERT_NOTENOUGHFUND = 260031;
	//! ��֧�ֵĶ�������
	const int TAPIERROR_ORDERINSERT_ORDERTYPE = 260032;
	//! ��֧�ֵ�ʱ����Ч����
	const int TAPIERROR_ORDERINSERT_TIMEINFORCE = 260033;
	//! ��֧�ֵĲ��Ե�����
	const int TAPIERROR_ORDERINSERT_NO_TACTICS = 260034;
	//! ƽ�������������гֲ���
	const int TAPIERROR_ORDERINSERT_POSITION_CANNOT_CLOSE = 260035;
	//! �µ��Զ����ʧ��
	const int TAPIERROR_ORDERINSERT_AUTOCHECK_FAIL = 260036;
	//! LMEδ׼������
	const int TAPIERROR_ORDERINSERT_LME_NOTREADY = 260037;
	//! ƽ�ַ�ʽ����
	const int TAPIERROR_ORDERINSERT_CLOSEMODE = 260038;
	//! �µ���Ӧ�ĸ��˺��ʽ���
	const int TAPIERROR_ORDERINSERT_PARENTNOTENOUGHFUND = 260039;
	//! �������ĺ�Լ��ʽ����
	const int TAPIERROR_SWAP_CONTRACT = 260040;
    //! ί�м۸񲻺���
    const int TAPIERROR_ORDERINSERT_PRICE = 260041;
    //! ��ƽ��ǲ�����
    const int TAPIERROR_ORDERINSERT_EFFECT = 260042;
    //! ������Լ����
    const int TAPIERROR_ORDERINSERT_TARGETCONTRACT = 260043;
	//! ��ǰ�ͻ�����ʹ�ô��˺Ž���
	const int TAPIERROR_USERNO_NOTHAS_ACCOUNT = 260051;
	//! ����ͨ��״̬������
	const int TAPIERROR_UPPERCHANNEL_BROKEN = 260052;
	//! ����ͨ��δ��ͨEXIST
	const int TAPIERROR_UPPERCHANNEL_NOT_EXIST = 260053;
	//! �����޴�ϵͳ��
	const int TAPIERROR_ORDERDELETE_NOT_SYSNO = 260061;
	//! ��״̬��������
	const int TAPIERROR_ORDERDELETE_NOT_STATE = 260062;
	//! ��״̬��������
	const int TAPIERROR_ORDERACTIVE_NOT_STATE = 260063;
	//! ֻ����������Լ����һ��ί��
	const int TAPIERROR_ORDERDELETE_NOT_LAST = 260064;
	//! ��״̬��ֹ���
	const int TAPIERROR_ORDERCHECK_NOT_STATE = 260071;
	//! �������ʧ��
	const int TAPIERROR_ORDERCHECK_FAIL = 260072;
	//! ��״̬������ĵ�
	const int TAPIERROR_ORDERMODIFY_NOT_STATE = 260081;
	//! �˹���������ĵ�
	const int TAPIERROR_ORDERMODIFY_BACK_INPUT = 260082;
	//! �����Ѳ�������
	const int TAPIERROR_ORDERINSERT_FEE = 260091;
	//! ��֤���������
	const int TAPIERROR_ORDERINSERT_MARGIN = 260092;
	//! �����˺�ֻ�ɲ�ѯ
	const int TAPIERROR_ORDER_NO_PERMIT = 260100;
	//! �������̲���Ӧ��
	const int TAPIERROR_RSPQUOTE_NO_PERMIT = 260101;
	//! �������ʺ����������̲���Ӧ��
	const int TAPIERROR_RSPQUOTE_CHILD_NO_PERMIT = 260102;
	//! �µ��Ҳ������ױ���
	const int TAPIERROR_TRADENO_NOT_FIND = 260103;
	//! �����˺�ֻ�ɿ���
	const int TAPIERROR_ORDER_NO_CLOSE = 260104;
	//! �����˺�û�����ڹҵ���ѯȨ��
	const int TAPIERROR_QRY_QUOTE_NO_PERMIT = 260105;
	//! ������Ч������С�ڵ�ǰ������
	const int TAPIERROR_EXPIREDATE_NO_PERMIT = 260106;
	//! �ñ��벻��������������
	const int TAPIERROR_CMB_NO_PERMIT = 260107;
	//! �Ǳ�����������µ��˺Ų��������
	const int TAPIERROR_ORDERSERVER_NO_PERMIT = 260108;
	//! ��Ȩ����Ȩ������������
	const int TAPIERROR_POSITION_CANNOT_EXEC_OR_ABANDON = 260109;
	//! û�ж������Ȩ��
	const int TAPIERROR_ORDERCHECK_NO_PERMIT = 260110;
	//! ����������󿪲���
	const int TAPIERROR_ORDERMAXOPENVOL_NO_PERMIT = 260111;
	//! �ǵ�ͣ������ֹ���򿪲�
	const int TAPIERROR_ORDERLIMIT_OPEN_NO_PERMIT = 260112;
	//! ������������µ���
	const int TAPIERROR_ORDER_SINGLEVOL_NO_PERMIT = 260113;
	//! �������ֲ���
	const int TAPIERROR_ORDER_POSITIONVOL_NO_PERMIT = 260114;
	//! �Ǵ���Ӧ�۵�����������ί������һ��
	const int TAPIERROR_ORDER_QTY_NO_PERMIT = 260115;
	//! ���ʺŲ�������������
	const int TAPIERROR_ORDER_CMB_CHILD_NO_PERMIT = 260116;
	//! ���벻�����ظ��ύ
	const int TAPIERROR_ORDER_APPLY_NO_PERMIT = 260117;
	//! �����˺��µ�Ƶ������
	const int TAPIERROR_ORDER_FREQ_OVERRUN = 260118;
	//! ��ϱ����ڵ���Ϸ����Ͷ����־
	const int TAPIERROR_COMB_NO_SIDEORHEDGE = 260119;
	//! ��ǰ��Ȩ���ں���۲��Ҫѯ��
	const int TAPIERROR_REQQUOTE_EXITREASONABLPRICE = 260120;
    //! Ӧ��ί�м۸񲻺���
    const int TAPIERROR_RSPQUOTE_PRICE = 260121;
    //! ��ͨ�ͻ���������ǿƽ��
    const int TAPIERROR_RISKORDER_CANCEL = 260122;
    //! Ӧ��ί�п�ƽ��־����ȷ
    const int TAPIERROR_RSPQUOTE_EFFECT = 260123;
    //! ������ʽ����
    const int TAPIERROR_ORDERINSERT_SIDEMODE = 260124;
    //! �Զ����������ί������
    const int TAPIERROR_AUTOORDER_MAXCOUNT = 260125;
    //! ��������������ѯ���󳬹���������
    const int TAPIERROR_SHFEDEEPQUOTE_LIMIT = 260126;
    //! ��������������ѯ����û������
    const int TAPIERROR_SHFEDEEPQUOTE_NODATA = 260127;
    //! �����Գɽ�����
    const int TAPIERROR_SELFMATCH = 260128;
    //! �������������
    const int TAPIERROR_ERRORORDER_MAXCOUNT = 260129;
    //! ����ϯλ�µ�Ƶ������
    const int TAPIERROR_ORDER_UPPERFREQ_OVERRUN = 260130;
    //! �ͻ���ֹ��ǰ����ί��
    const int TAPIERROR_ORDERTYPE_LIMIT = 260131;


	//! �ʽ��˺Ų�����
	const int TAPIERROR_IORDERINSERT_ACCOUNT = 160001;
	//! �ʽ��˺�״̬����ȷ
	const int TAPIERROR_IORDERINSERT_ACCOUNT_STATE = 160002;
	//! �ʽ��˺Ž������Ĳ�һ��
	const int TAPIERROR_IORDERINT_ACC_TRADECENT_ERROR = 160003;
	//! ���˺Ų������µ�
	const int TAPIERROR_IORDERINT_MAINACCOUNT_ERROR = 160004;
	//! ���˺���Ϣ����
	const int TAPIERROR_IORDERINT_MAINACCINFO_ERROR = 160005;
	//! �˺Ž�ֹ��Ȩ�м��µ�
	const int TAPIERROR_IORDERINT_NO_OPTMARKET_ERROR = 160006;
    //! Ŀǰ��֧�ֵ�ָ��
    const int TAPIERROR_IORDERINT_UN_SUPPORT_ERROR = 160007;
	//! �µ���Ч�ĺ�Լ(����)
	const int TAPIERROR_IORDERINSERT_CONTRACT = 160011;
	//! LMEδ׼������(����)
	const int TAPIERROR_IORDERINSERT_LME_NOTREADY = 160012;
	//! ��֧�ֵ��µ�����
	const int TAPIERROR_ORDERINSERT_ERROR_ORDER_TYPE = 160013;
	//! �����������
	const int TAPIERROR_IORDERINSERT_READY_TYPE_ERROR = 160014;
	//! ���Ϸ���ί������
	const int TAPIERROR_IORDERINSERT_ORDER_TYPE_ERROR = 160015;
    //! �µ���Լ��ĺ�Լ������
    const int TAPIERROR_IORDERINSERT_SUBCONTRACT = 160016;
    //! �ֻ��µ�������������
    const int TAPIERROR_IORDERINSERT_SPOTBUYQTY = 160017;
    //! ���Ϲ���Ȩ��������
    const int TAPIERROR_IORDERINSERT_RESERVE_PUT = 160018;
    //! ���뿪�ֲ�������
    const int TAPIERROR_IORDERINSERT_RESERVE_B_OPEN = 160019;
    //! ����ƽ�ֲ�������
    const int TAPIERROR_IORDERINSERT_RESERVE_S_COVER	= 160020;
	//! �ͻ�Ȩ�޽�ֹ����
	const int TAPIERROR_ORDER_NOTRADE_ACCOUNT = 160021;
	//! �ͻ�Ʒ�ַ����ֹ����
	const int TAPIERROR_ORDER_NOTRADE_COM_GROUP = 160022;
	//! �ͻ���Լ�����ֹ����
	const int TAPIERROR_ORDER_NOTRADE_ACC_CONTRACT = 160023;
	//! ϵͳȨ�޽�ֹ����
	const int TAPIERROR_ORDER_NOTRADE_SYSTEM = 160024;
	//! �ͻ�Ȩ��ֻ��ƽ��
	const int TAPIERROR_ORDER_CLOSE_ACCOUNT = 160025;
	//! �ͻ���Լ����ֻ��ƽ��
	const int TAPIERROR_ORDER_CLOSE_ACC_CONTRACT = 160026;
	//! ϵͳȨ��ֻ��ƽ��
	const int TAPIERROR_ORDER_CLOSE_SYSTEM = 160027;
	//! ֻ��ƽ����ǰ��������ֻ��ƽ��
	const int TAPIERROR_ORDER_CLOSE_DAYS = 160028;
	//! �ͻ�Ʒ�ַ��Ȩ�޽�ֹ����
	const int TAPIERROR_ORDER_NOTRADE_RISK = 160029;
	//! �ͻ�Ʒ�ַ��Ȩ��ֻ��ƽ��
	const int TAPIERROR_ORDER_CLOSE_RISK = 160030;
	//! ��Լ��ֲ��������������
	const int TAPIERROR_IORDERINSERT_POSITIONMAX = 160031;
	//! �µ��������������
	const int TAPIERROR_ORDERINSERT_ONCEMAX = 160032;
	//! �µ���Լ�޽���·��(����)
	const int TAPIERROR_IORDERINSERT_TRADEROUTE = 160033;
	//! ί�м۸񳬳�ƫ�뷶Χ
	const int TAPIERROR_ORDER_IN_MOD_PRICE_ERROR = 160034;
	//! ����GiveUp���ֲ���
	const int TAPIERROR_ORDER_IN_GIVEUP_POS_MAX = 160035;
    //! �ֲ�������ETF�ֲܳ�����
    const int TAPIERROR_ORDER_ETF_POSITIONMAX = 160036;
    //! �ֲ�������ETFȨ��������
    const int TAPIERROR_ORDER_ETF_BUYPOSITIONMAX = 160037;
    //! �ֲ�������ETF�������뿪������
    const int TAPIERROR_ORDER_ETF_BUYONEDAYPOSITIONMAX = 160038;
    //! ���������ֻ�����
    const int TAPIERROR_ORDERINSERT_NOTENOUGHSPOT = 160039;
    //! �ֻ���֧�ֱ���
    const int TAPIERROR_ORDERINSERT_RESERVE_SPOT = 160040;
	//! δ��¼����
	const int TAPIERROR_UPPERCHANNEL_NOT_LOGIN = 160041;
	//! δ�ҵ�������Ϣ
	const int TAPIERROR_UPPERCHANNEL_NOT_FOUND = 160042;
    //! ��Ʒ�ֲ�֧�ֽ���������
    const int TAPIERROR_COMMODITY_LOCK = 160043;
    //! �ֻ�δ���ö�Ӧ��ȨƷ��
    const int TAPIERROR_SPOT_ROOT_COMMODITY = 160044;
    //! �ֻ���Ӧ��Ȩ�޽���·��
    const int TAPIERROR_SPOT_ROOTCOM_TRADEROUTE = 160045;
	//! �µ��ʽ���(����)
	const int TAPIERROR_IORDERINSERT_NOTENOUGHFUND = 160051;
	//! �����Ѳ�������(����)
	const int TAPIERROR_IORDERINSERT_FEE = 160052;
	//! ��֤���������(����)
	const int TAPIERROR_IORDERINSERT_MARGIN = 160053;
	//! �ܻ����ʽ���
	const int TAPIERROR_ORDERINSERT_BASENOFUND = 160054;
	//! ������֤����
	const int TAPIERROR_ORDERINSERT_MARGINAMOUNT = 160055;
	//! �ܻ��ҳ������ֱ�������
	const int TAPIERROR_ORDERINSERT_OPENRATIO = 160056;
	//! ���������鳬�����ֱ�������
	const int TAPIERROR_ORDERINSERT_GROUP_OPENRATIO = 160057;
	//! �������в�������
	const int TAPIERROR_ORDERINSERT_RISKARRAY = 160058;
    //! �ܻ��ҳ����޹��������
    const int TAPIERROR_ORDERINSERT_BUYLIMITE = 160059;
    //! ���������鳬���޹��������
    const int TAPIERROR_ORDERINSERT_GROUP_BUYLIMITE = 160060;

	//! �����޴�ϵͳ��(����)
	const int TAPIERROR_IORDERDELETE_NOT_SYSNO = 160061;
	//! ��״̬��������(����)
	const int TAPIERROR_IORDERDELETE_NOT_STATE = 160062;
	//! ¼����������
	const int TAPIERROR_ORDERDELETE_NO_INPUT = 160063;
    //! ������������/����ָ��
    const int TAPIERROR_ORDERDELETE_NO_TRADE = 160064;
	//! ��״̬������ĵ�(����)
	const int TAPIERROR_IORDERMODIFY_NOT_STATE = 160071;
	//! �˹���������ĵ�(����)
	const int TAPIERROR_IORDERMODIFY_BACK_INPUT = 160072;
	//! ���ձ���������ĵ�
	const int TAPIERROR_ORDERMODIFY_RISK_ORDER = 160073;
	//! �ɽ������ڸĵ���
	const int TAPIERROR_ORDERMODIFY_ERROR_QTY = 160074;
	//! Ԥ�񵥲�����ĵ�
	const int TAPIERROR_ORDERMODIFY_ERROR_READY = 160075;
	//! ��ɾ����������ת��
	const int TAPIERROR_ORDERINPUT_CANNOTMOVE = 160081;
	//! ¼���ظ�
	const int TAPIERROR_ORDERINPUT_REPEAT = 160091;
	//! ��Լ����۸��޸�ʧ��
	const int TAPIERROR_CONTRACT_QUOTE = 160101;
	//! �µ��������ֵ��������
	const int TAPIERROR_UPPER_ONCEMAX = 160111;
	//! �µ������������ֲ���
	const int TAPIERROR_UPPER_POSITIONMAX = 160112;
    //! Ʒ���ֲܲ����ֲ�������
    const int TAPIERROR_ORDERINSERT_POSMAX_COM = 160113;
    //! Ʒ�־��ֲ����ֲ�������
    const int TAPIERROR_ORDERINSERT_POSMAX_COM_NET = 160114;
	//! ��ƽ��ʽ����
	const int TAPIERROR_IORDERINSERT_CLOSEMODE = 160121;
	//! ί��ƽ�ֲֲֳ���
	const int TAPIERROR_CLOSE_ORDER = 160122;
	//! �ɽ�ƽ��ʧ��
	const int TAPIERROR_CLOSE_MATCH = 160123;
    //! �ֻ�ƽ�ֳ���������
    const int TAPIERROR_CLOSE_SPOT_OUT_LOCK = 160124;
    //! �ֻ����һ���Ϊ��
    const int TAPIERROR_CLOSE_SPOT_OUT_NULL = 160125;
	//! δ�ҵ�����ί��
	const int TAPIERROR_MOD_DEL_NO_ORDER = 160131;
	//! �����ضϿ�����
	const int TAPIERROR_MOD_DEL_GATEWAY_DISCON = 160132;
	//! ¼���ɽ��ظ�
	const int TAPIERROR_MATCHINPUT_REPEAT = 160141;
	//! ¼���ɽ�δ�ҵ���Ӧί��
	const int TAPIERROR_MATCHINPUT_NO_ORDER = 160142;
	//! ¼���ɽ���Լ������
	const int TAPIERROR_MATCHINPUT_NO_CONTRACT = 160143;
	//! ¼���ɽ���������
	const int TAPIERROR_MATCHINPUT_PARM_ERROR = 160144;
	//! ¼���ɽ�ί��״̬����
	const int TAPIERROR_MATCHINPUT_OSTATE_ERROR = 160145;
    //! ¼���ɽ���ƽ��־����
    const int TAPIERROR_MATCHINPUT_OCMODE_ERROR = 160146;
	//! �ɽ�ɾ��δ�ҵ��ɽ�
	const int TAPIERROR_MATCHREMOVE_NO_MATCH = 160151;
	//! ��״̬�ɽ�����ɾ
	const int TAPIERROR_MATCHREMOVE_STATE_ERROR = 160152;
	//! ������¼���״̬����
	const int TAPIERROR_ORDERINPUT_STATE_ERROR = 160161;
	//! ������޸Ķ�������
	const int TAPIERROR_ORDERINPUT_MOD_ERROR = 160162;
	//! ��������ɾ�����ڶ�Ӧ�ɽ�
	const int TAPIERROR_ORDERREMOVE_ERROR = 160163;
	//! ���Ϸ���ί��״̬
	const int TAPIERROR_ORDERINPUT_MOD_STATE_ERROR = 160164;
	//! ��״̬��������ת��
	const int TAPIERROR_ORDEREXCHANGE_STATE_ERROR = 160165;
	//! ����������ɾ��
	const int TAPIERROR_ORDERREMOVE_NOT_ERROR = 160166;
	//! ������˫�߳���δ�ҵ�ί��
	const int TAPIERROR_ORDERMARKET_DELETE_NOTFOUND = 160171;
	//! ������˫�߳����ͻ���һ��
	const int TAPIERROR_ORDERMARKET_DEL_ACCOUNT_NE = 160172;
	//! ������˫�߳���Ʒ�ֲ�һ��
	const int TAPIERROR_ORDERMARKET_DEL_COMMODITY_NE = 160173;
	//! ������˫�߳�����Լ��һ��
	const int TAPIERROR_ORDERMARKET_DEL_CONTRACT_NE = 160174;
	//! ������˫�߳�������������ͬ
	const int TAPIERROR_ORDERMARKET_DEL_SIDE_EQ = 160175;
	//! ������˫�߳��������������
	const int TAPIERROR_ORDERMARKET_DEL_SIDE_ERROR = 160176;
	//! �����̵��߼��δͨ��
	const int TAPIERROR_ORDERMARKET_OTHER_SIDE_ERROR = 160177;
	//! �񵥼���ʧ�ܣ�����δ�ҵ�
	const int TAPIERROR_ORDERACTIVATE_NOTFOUND_ERROR = 160181;
	//! �񵥼���ʧ�ܣ�����Ч״̬
	const int TAPIERROR_ORDERACTIVATE_STATE_ERROR = 160182;
    //! ���𼤻�ʧ�ܣ����ز�֧��
    const int TAPIERROR_ORDERACTIVATE_GATEWAY_ERROR = 160183;
    //! ����Ա�޿������µ�Ȩ��
    const int TAPIERROR_TRANSIT_ORDERINSERT_RIGHT = 160191;
    //! δ������ת����
    const int TAPIERROR_TRANSIT_ORDERINSERT_DISCON = 160192;
    //! �µ�δ����Ŀ�꽻������
    const int TAPIERROR_TRANSIT_ORDERINSERT_DISCON_DEST	= 160193;
    //! ����δ����Ŀ�꽻������
    const int TAPIERROR_TRANSIT_ORDERDELETE_DISCON_DEST	= 160194;
    //! �ĵ�δ����Ŀ�꽻������
    const int TAPIERROR_TRANSIT_ORDERMODIFY_DISCON_DEST	= 160195;
    //! �������ת��������
    const int TAPIERROR_TRANSIT_ORDER_OPERATOR = 160196;
    //! �ͻ�Ȩ�޽�ֹ����
    const int TAPIERROR_ORDER_DISALLOWBUY_ACCOUNT = 160201;
    //! �ͻ�Ȩ�޽�ֹ����
    const int TAPIERROR_ORDER_DISALLOWSELL_ACCOUNT = 160202;
    //! ϵͳȨ�޽�ֹ����
    const int TAPIERROR_ORDER_DISALLOWBUY_SYSTEM = 160203;
    //! ϵͳȨ�޽�ֹ����
    const int TAPIERROR_ORDER_DISALLOWSELL_SYSTEM = 160204;
    //! �ͻ�Ȩ�޽�ֹ��������Ȩ -������ϵͳ
    const int TAPIERROR_ORDER_DIS_SELLOPTION_ACCOUNT = 160205;
    //! ϵͳȨ�޽�ֹ��������Ȩ -������ϵͳ
    const int TAPIERROR_ORDER_DIS_SELLOPTION_SYSTEM = 160206;
    //! �Ǳ�׼��Լֻ��ƽ��
    const int TAPIERROR_ORDER_CONTRACT_CLOSE = 160207;
    //! ���������޶�
    const int TAPIERROR_ORDERINSERT_LOANAMOUNT = 160211;

    //! ��Ʒ�ֲ�֧����ϲ���
    const int TAPIERROR_COMBINE_COMMODITY = 160220;
    //! ����걨��Լ��Ȩ���Ͳ�����Ҫ��
    const int TAPIERROR_COMBINE_CALLORPUT = 160221;
    //! ��ֵ���ϳֲֲ�����
    const int TAPIERROR_COMBINE_COMPOSITION = 160222;
    //! ��ֵ���ϳֲ���������
    const int TAPIERROR_COMBINE_COMPOSITION_QTY = 160223;
    //! ����걨��Լ���ұ�ʶ������Ҫ��
    const int TAPIERROR_COMBINE_HEDGEFLAG = 160224;
    //! ����걨��Լ�������򲻷���Ҫ��
    const int TAPIERROR_COMBINE_ORDERSIDE = 160225;
    //! ����걨��Լ��С������Ҫ��
    const int TAPIERROR_COMBINE_CONTRACTSIZE = 160226;
    //! ����걨��Լ�����ղ�����Ҫ��
    const int TAPIERROR_COMBINE_CONTRACTDAYS = 160227;
    //! ����걨��Լ��Ȩ�۲�����Ҫ��
    const int TAPIERROR_COMBINE_STRIKEPRICE = 160228;
    //! ��ͬ��Լ���������
    const int TAPIERROR_COMBINE_CONTRACT_SAME = 160229;
    
    //! ���ҽ���������
    const int TAPIERROR_ORDERINSERT_UNLOCK_NOE = 160230;
    //! ��Ȩ���ֱ���������
    const int TAPIERROR_ORDEROPEN_OPT_SPOT_NOE = 160231;
    //! ��Ȩƽ�ֱ���������
    const int TAPIERROR_ORDERCLOSE_OPT_SPOT_NOE = 160232;
    //! ��Ч�ı��Ҷ���
    const int TAPIERROR_ORDERINSERT_COVERED_UNVLD = 160233;

	//! ��������Ƶ�ʹ���
	const int TAPIERROR_ORDER_FREQUENCY = 61001;
	//! ί�в�ѯ����ǰ���ܽ����´β�ѯ
	const int TAPIERROR_ORDER_QUERYING = 61002;

    //! ǰ�ò������ģ���¼
    const int TAPIERROR_TRADEFRONT_MODULETYPEERR = 190001;
    //! һ������̫������
    const int TAPIERROR_TRADEFRONT_TOOMANYDATA = 190002;
    //! ǰ��û����Ҫ����
    const int TAPIERROR_TRADEFRONT_NODATA = 190003;
    //! ����ѯ�Ĳ���Ա��Ϣ������
    const int TAPIERROR_TRADEFRONT_NOUSER = 190004;
    //! ǰ���뽻�׶Ͽ�
    const int TAPIERROR_TRADEFRONT_DISCONNECT_TRADE = 190011;
    //! ǰ�������Ͽ�
    const int TAPIERROR_TRADEFRONT_DISCONNECT_MANAGE = 190012;
    //! �����ʽ��˺Ų�����
    const int TAPIERROR_TRADEFRONT_ACCOUNT = 190021;
    //! �ò���Ա��������
    const int TAPIERROR_TRADEFRONT_ORDER = 190022;
    //! ��ѯƵ�ʹ���
    const int TAPIERROR_TRADEFRONT_FREQUENCY = 190023;
    //! ����Ȩ�������¼
    const int TAPIERROR_TRADEFRONT_RUFUSE = 190024;
    //! �Գɽ���֤��ͨ��
    const int TAPIERROR_TRADEFRONT_SELFMATCH = 190025;
    //! �ǽ���Ա������ǿƽ��
    const int TAPIERROR_TRADEFRONT_DELETEFORCE = 190026;
	/** @}*/

	//=============================================================================
	/**
	 *	\addtogroup G_ERR_CELPHONE �ֻ����淵�ش�����
	 *	@{
	 */
	//==============================================================================
	//! ��Աϵͳ��ַ��Ϣ������
	const int TAPIERROR_AddressLoss = 990001;
	//! ϵͳ��δ��¼
	const int TAPIERROR_UnLogin = 990002;
	//! ��֤��Ϣ����ʧ��
	const int TAPIERROR_AuthEncryptFail = 990003;
	//! ����δ������Ч�ĺ�̨
	const int TAPIERROR_ChannelCreateFail = 990004;
	//! ����δ����
	const int TAPIERROR_ChannelUnready = 990005;
	//! Э���ʽ����
	const int TAPIERROR_PtlFmtError = 990006;
	//! ���Ե�����δ����
	const int TAPIERROR_StrategyInactive = 990007;
	//! ���Ե��������ڳ�ʼ����
	const int TAPIERROR_StrategyIniting = 990008;
	//! �������
	const int TAPIERROR_PwdFail = 990009;
	//! δ�ҵ�ԭ������
	const int TAPIERROR_NoUser = 990010;
	//! ��¼������
	const int TAPIERROR_OnlineCountFail = 990011;
	//! ���Ե��ѵ�¼
	const int TAPIERROR_StrategyLogined = 990012;
	//! �����µ�¼
	const int TAPIERROR_ReLogin = 990013;
	//! ����ʱ�޷��ҵ�����ί�м�
	const int TAPIERROR_NoPrice = 990101;
	//! �޷�ʶ��Ĳ��Ե�
	const int TAPIERROR_NoStrategy = 990102;
	//! �޷��ҵ�������
	const int TAPIERROR_NoParentOrder = 990103;
	//! ��������ʧ���ӵ�ʧЧ
	const int TAPIERROR_ParentOrderFail = 990104;
	//! ���Ե�δ��д������
	const int TAPIERROR_NoTradeDate = 990105;
	//! ���Ե�����δ�ҵ�ԭ����
	const int TAPIERROR_NoOrderNo = 990106;
	//! ��ƽ������
	const int TAPIERROR_CannotClose = 990107;
	//! ���Ե���������
	const int TAPIERROR_ImmediateTrigger = 990108;
	//! ���Ե���������
	const int TAPIERROR_OrderUnusual = 990109;
	//! û������ĺ�Լ
	const int TAPIERROR_NoQuote = 990110;
	//! ��֧�ֵĲ���
	const int TAPIERROR_UnsupportedAction = 990201;
	//! �ڻ���˾��ַ�޷�����
	const int TAPIERROR_InvalidAddress = 990202;
	//! ��֧�ֽ���Ա��¼
	const int TAPIERROR_UnsupportedLoginNo = 990203;
	//! �������
	const int TAPIERROR_GwPwdFail = 990204;
	//! ��������������
	const int TAPIERROR_PwdFailLimit = 990205;
	//! ����������ʱ��
	const int TAPIERROR_InvalidMarketState = 990206;
	//! ǿ���޸�����
	const int TAPIERROR_ForceChangePwd = 990207;
	//! ��¼������
	const int TAPIERROR_LoginCount = 990208;
	//! ��֧�ֵĺ�Լ
	const int TAPIERROR_UnsupportedContract = 990301;
	//! ��֧�ֵĶ�������
	const int TAPIERROR_UnsupportedOrderType = 990302;
	//! �ֲֲ���ƽ
	const int TAPIERROR_InadequatePosiQty = 990303;
	//! �ʽ���
	const int TAPIERROR_InadequateMoney = 990304;
	//! �۸����ǵ�ͣ��Χ
	const int TAPIERROR_UnsupportedPrice = 990305;
	//! �۸񶩵���������
	const int TAPIERROR_UnsupportedActType = 990306;
	//! ��ί��״̬�޷�����
	const int TAPIERROR_CancelState = 990307;
	//! �����ֶ�����
	const int TAPIERROR_OrderFieldErr = 990308;
	//! �µ��˺����¼�˺Ų�һ��
	const int TAPIERROR_UnsupportedAcc = 990309;
	//! ί�в�����
	const int TAPIERROR_UnsupportedOrder = 990310;
	//! ��֧�ֵı���
	const int TAPIERROR_UnsupportedCurrency = 990311;
	//! ���͵�¼����ʧ��
	const int TAPIERROR_SendLoginFail = 990312;
	//! �ǽ���ʱ��
	const int TAPIERROR_InvalidTime = 990313;
	//! ��Ȩ/��Ȩ����������
	const int TAPIERROR_InadequateExecQty = 990314;

	/** @}*/
    
    //=============================================================================
    /**
     *	\addtogroup G_ERR_GATEWAY �������ش������	
     *	@{
     */
    //=============================================================================
    //! ��������ʧ��
    const int TAPIERROR_ORDER_SEND                                         = 280001;
    //! ���ͱ���ʧ�ܣ�����û���ӵ�������
    const int TAPIERROR_DLG_NULL                                           = 280002;
    //! �����ֶ�����
    const int TAPIERROR_ORDER_FIELD                                        = 280003;
    //! �����־ܾ�
    const int TAPIERROR_TRADE_REJ_BYUPPER                                  = 280004;
    //! ��ǰʱ�䲻��������Ȩ����
    const int TAPIERROR_ORDER_FORBIDEXEC                                   = 280005;
	//! ����δ������δ��������
	const int TAPIERROR_GW_NOT_READY                                       = 180001;
	//! Ʒ�ִ���
	const int TAPIERROR_GW_INVALID_COMMODITY                               = 180002;
	//! ��Լ����
	const int TAPIERROR_GW_INVALID_CONTRACT                                = 180003;
	//! �����ֶ�����
	const int TAPIERROR_GW_INVALID_FIELD                                   = 180004;
	//! �۸񲻺Ϸ�
	const int TAPIERROR_GW_INVALID_PRICE                                   = 180005;
	//! �������Ϸ�
	const int TAPIERROR_GW_INVALID_VOLUME                                  = 180006;
	//! �������Ͳ��Ϸ�
	const int TAPIERROR_GW_INVALID_TYPE                                    = 180007;
	//! ί��ģʽ���Ϸ�
	const int TAPIERROR_GW_INVALID_MODE                                    = 180008;
	//! ί�в����ڣ��ĵ���������
	const int TAPIERROR_GW_ORDER_NOT_EXIST                                 = 180009;
	//! ���ͱ���ʧ��
	const int TAPIERROR_GW_SEND_FAIL                                       = 180010;
	//! �����־ܾ�
	const int TAPIERROR_GW_REJ_BYUPPER                                     = 180011;

    /** @}*/
}

#endif /* ESTRADEAPIERROR_H */
