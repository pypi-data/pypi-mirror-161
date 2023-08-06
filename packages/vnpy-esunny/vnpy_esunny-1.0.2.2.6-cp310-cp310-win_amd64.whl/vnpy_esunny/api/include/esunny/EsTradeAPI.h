//============================================================================
/* ����ʢͳһ����API�ӿ�
 * ���ļ�������EsTradeAPI ʹ�õĽӿں����͹���
 * �汾��Ϣ:2018-05-21 ������ �������ļ�
 */
//=============================================================================
#ifndef ES_TRADE_API_H
#define ES_TRADE_API_H

#include "EsTradeAPIStruct.h"

#if defined WIN32 || defined _WIN64
#define ES_CDECL __cdecl
#define ES_DLLEXPORT __declspec(dllexport)
#else
#define ES_CDECL
#define ES_DLLEXPORT
#endif

//EsTradeAPI.h
//�ļ�������EsTradeAPI�ṩ�������ߵĶ���ӿڡ������ͻص��ӿڡ�
namespace EsTradeAPI
{
    
//EsTradeAPI�Ļص�֪ͨ�ӿ�
class IEsTradeAPINotify
{
public:
	/**
	* @brief ĳһ����¼�û����ӳɹ��ص�֪ͨ
	* @param[in] UserNo ��¼�û�UserNo
    * 
	* @ingroup G_T_Login
	*/
	virtual void ES_CDECL OnConnect(const TAPISTR_20 UserNo) = 0;
	/**
	* @brief	ϵͳ��¼���̻ص�
	* @details	�˺���ΪStartUser()��¼�����Ļص�������StartUser()�ɹ����������ӣ�Ȼ��API������������͵�¼��֤��Ϣ����¼�ڼ�����ݷ�������͵�¼�Ļ�����Ϣ���ݵ��˻ص������С�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nErrorCode ���ش�����,0��ʾ�ɹ�
	* @param[in] pLoginRspInfo ��½Ӧ����Ϣ�����nErrorCode!=0����loginRspInfo=NULL��
	* @attention	�ûص����سɹ���˵���û���¼�ɹ������ǲ�����ǰ��¼�û�׼����ϡ�
    * 
	* @ingroup G_T_Login
	*/
	virtual void ES_CDECL OnRspLogin(const TAPISTR_20 UserNo, TAPIINT32 nErrorCode, const TapAPITradeLoginRspInfo *pLoginRspInfo) = 0;
	/**
	* @brief	������֤��ϵ��ʽ֪ͨ��(�����ǡ���Ʊר��)
	* @details	��¼��ɺ������Ҫ������֤�����յ���ϵ��ʽ��֪ͨ������ѡ��֪ͨ��Ϣ��һ����ϵ��ʽ��������ߵ绰��,�����Ͷ�����֤��Ȩ�롣
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nErrorCode ���ش�����,0��ʾ�ɹ�
	* @param[in] isLast ��ʶ�Ƿ������һ����ϵ��Ϣ
	* @param[in] pInfo ��֤��ʽ��Ϣ�����errorCode!=0����ContactInfoΪ�ա�
	* @attention	�ûص����سɹ���˵����Ҫ������֤��������Ҫѡ��һ����ϵ��ʽȻ�����RequestVertificateCode()���ý�����֤��Ϣ�ķ�ʽ���˺š�
	*
    * @ingroup G_T_Login
	*/
	virtual void ES_CDECL OnRtnContactInfo(const TAPISTR_20 UserNo, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPISecondInfo* pInfo) = 0;
	/**
	* @brief	�����Ͷ�����֤��Ӧ��(�����ǡ���Ʊר��)
	* @details	�����ȡ������֤��Ȩ�룬��̨�����ʼ����߶��ţ�������Ӧ�𣬰�����������Լ���֤����Ч��
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nSessionID ���������֤��ỰID
	* @param[in] nErrorCode ���û�а���ϵ�����ش���.
	* @param[in] isLast ��ʶ�Ƿ������һ����ϵ��Ϣ
	* @param[in] pInfo ������֤����Ч�ڣ��Է��ӷ��أ��ڶ�����֤��Ч���ڣ������ظ����ö�����֤�룬���ǲ������������������֤�롣
	* @attention �ûص����سɹ���Ȼ�����SetVertificateCode()��
    * 
	* @ingroup G_T_Login
	*/
	virtual void ES_CDECL OnRspRequestVertificateCode(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIVertificateCode *pInfo) = 0;
	/**
     * @brief	��֤��ϢӦ��(�����ǡ���Ʊר��)
	 * @details	 ��������ʱ������Ҫͨ�������֤����֤ͨ���ſ��Է�����֤��������֤ʧ�ܿ������·�����֤����
     * @param UserNo ��¼�û�UserNo
     * @param nSessionID ��֤��Ϣ�ỰID
     * @param nErrorCode ������,0��ʾ�ɹ�
     * @param isLast ��ʶ�Ƿ������һ����Ϣ
     * @param pInfo ��֤��ϢӦ��
     * @attention �ûص����سɹ���Ȼ�����RequestVertificateCode()��
     * 
	 * @ingroup G_T_Login
     */
    virtual void ES_CDECL OnRspRequestVerifyIdentity(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIVerifyIdentity* pInfo) = 0;
    /**
     * @brief	��֤������Ӧ��(�����ǡ���Ʊר��)
     * @param UserNo ��¼�û�UserNo
     * @param nSessionID ������֤��ỰID
     * @param nErrorCode ������,0��ʾ�ɹ�
     * @param isLast ��ʶ�Ƿ������һ����Ϣ
     * @param pInfo ��֤����Ϣ
     * 
	 * @ingroup G_T_Login
     */
    virtual void ES_CDECL OnRspSetVertificateCode(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPISecondCertificationRsp *pInfo) = 0;
    /**
	* @brief ��Ҫ������Ϣ��ʾ
	* @details ��API�ڲ��������ش���ʱ��ʾ�û�������Ϣ
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] ErrorMsg ������ʾ��Ϣ
	* @attention �ú����ص�����˵��API����ʱ�������ش���
    * 
	* @ingroup G_T_TradeSystem
	*/
	virtual void ES_CDECL OnRtnErrorMsg(const TAPISTR_20 UserNo, const TAPISTR_500 ErrorMsg) = 0;
	/**
	* @brief	֪ͨ�û�API׼������
	* @details	ֻ���û��ص��յ��˾���֪ͨʱ���ܽ��ж�Ӧ��¼�û������ĸ��ֲ������˻ص�������ĳ����¼�û��ܷ����������ı�־��
	* @param[in] UserNo ��¼�û�UserNo
	* @attention ������ſ��Խ��к�������
    * 
	* @ingroup G_T_Login
	*/
	virtual void ES_CDECL OnAPIReady(const TAPISTR_20 UserNo) = 0;
	/**
	* @brief API�ͷ���ʧȥ���ӵĻص�
	* @details ��APIʹ�ù������������߱��������������ʧȥ���Ӻ󶼻ᴥ���˻ص�֪ͨ�û���������������Ѿ��Ͽ���
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nReasonCode �Ͽ�ԭ�����
    * 
	* @ingroup G_T_Disconnect
	*/
	virtual void ES_CDECL OnDisconnect(const TAPISTR_20 UserNo, TAPIINT32 nReasonCode) = 0;
	/**
	* @brief ֪ͨ�û��ύ�û���¼��Ϣ���(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nSessionID �ύ�û���¼��Ϣ������ID,��SubmitUserLoginInfo���ص�����ID��Ӧ
	* @param[in] pRspInfo ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
    * 
	* @ingroup G_T_UserInfo
	*/
	virtual void ES_CDECL OnRspSubmitUserLoginInfo(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, const TapAPISubmitUserLoginInfoRsp *pRspInfo) = 0;
	/**
	* @brief �û������޸�Ӧ��
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nSessionID �޸����������ID,��ChangePassword������ID��Ӧ
	* @param[in] nErrorCode ���ش����룬0��ʾ�ɹ�
    * 
	* @ingroup G_T_UserInfo
	*/
	virtual void ES_CDECL OnRspChangePassword(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, TAPIINT32 nErrorCode, const TapAPIChangePasswordRsp* pInfo) = 0;
	/**
	* @brief �����û�Ԥ����Ϣ����
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nSessionID �����û�Ԥ����Ϣ������ID
	* @param[in] nErrorCode ���ش����룬0��ʾ�ɹ�
	* @param[in] info ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��info��ָʾ�����ݣ��������ý���������������Ч��
	* @note �ýӿ���δʵ��
    * 
	* @ingroup G_T_UserInfo
	*/
	virtual void ES_CDECL OnRspSetReservedInfo(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, TAPIINT32 nErrorCode, const TAPISTR_50 info) = 0;
	/**
	* @brief	����������Լ��Ϣ(�����ǡ�������ר��)
	* @details	���û������µĺ�Լ����Ҫ���������ڽ���ʱ����з�����������º�Լʱ�����û����������Լ����Ϣ��
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pRtnInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	* 
	* @ingroup G_T_Contract
	*/
	virtual void ES_CDECL OnRtnContract(const TAPISTR_20 UserNo, const TapAPITradeContractInfo *pRtnInfo) = 0;
	/**
	* @brief �û��ʽ�仯֪ͨ
	* @details �û���ί�гɽ���������ʽ����ݵı仯�������Ҫ���û�ʵʱ������
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
	* @note �������ע�������ݣ������趨Loginʱ��NoticeIgnoreFlag�����Ρ�
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_FundInfo
	*/
	virtual void ES_CDECL OnRtnFund(const TAPISTR_20 UserNo, const TapAPIFundData *pRtnInfo) = 0;
	/**
	* @brief ������ί�С����µĻ��������ط��µ����͹�����
	* @details ���������յ��ͻ��µ�ί�����ݺ�ͻᴥ��ί�д����߼���ͬʱ���û�����һ��ί��Ӧ��˵����������ȷ�������û������󣬷��ص���Ϣ�а�����ȫ����ί����Ϣ��
	*			ͬʱ��һ��������ʾ��ί�е�ί�кš�����Ǳ��ط���ȥ��ί�У�ί��Ӧ���л᷵������ID
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ĻỰID
	* @param[in] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
	* @note �������ע�������ݣ������趨Loginʱ��NoticeIgnoreFlag�����Ρ�
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
	*/
	virtual void ES_CDECL OnRtnOrder(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIOrderInfo *pRtnInfo) = 0;
	/**
    * @brief	��������Ӧ��(�����ǡ���Ʊר��)
    * @details	�µ����������ĵ�Ӧ���µ������д�Ӧ��ص�������µ�����ṹ��û����д��Լ�����ʽ��˺ţ�������ش����.
    *     �������ĵ�������Ӧ���OnRtnOrder���ɹ�������OnRtnOrder�ص���
    * @param[in] nRequestID ����ĻỰID
    * @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
    * @param[in] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
    * @attention ��Ҫ�޸ĺ�ɾ��pRtnInfo��ָʾ�����ݣ��������ý���������������Ч��
    *
    * @ingroup G_T_TradeActions
    */
    virtual void ES_CDECL OnRspOrderAction(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, const TapAPIOrderActionRsp *pRtnInfo) = 0;
    /**
	* @brief ���ز�ѯ��ί�б仯������Ϣ
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ĻỰID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast ��ʾ�Ƿ������һ������
	* @param[in] pRspInfo ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeInfo
	*/
	virtual void ES_CDECL OnRspQryOrderProcess(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIOrderInfo *pRspInfo) = 0;
	/**
	* @brief �������ĳɽ���Ϣ
	* @details �û���ί�гɽ������û����ͳɽ���Ϣ
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
	* @note �������ע�������ݣ������趨Loginʱ��NoticeIgnoreFlag�����Ρ�
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
	*/
	virtual void ES_CDECL OnRtnFill(const TAPISTR_20 UserNo, const TapAPIFillInfo *pRtnInfo) = 0;
	/**
	* @brief �ֱֲ仯����֪ͨ
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
	* @note �������ע�������ݣ������趨Loginʱ��NoticeIgnoreFlag�����Ρ�
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
	*/
	virtual void ES_CDECL OnRtnPosition(const TAPISTR_20 UserNo, const TapAPIPositionInfo *pRtnInfo) = 0;
	/**
	* @brief ƽ�����ݱ仯����(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
	* @note �������ע�������ݣ������趨Loginʱ��NoticeIgnoreFlag�����Ρ�
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
	*/
	virtual void ES_CDECL OnRtnClose(const TAPISTR_20 UserNo, const TapAPICloseInfo *pRtnInfo) = 0;
	/**
	* @brief �ֲ�ӯ��֪ͨ(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
	* @note �������ע�������ݣ������趨Loginʱ��NoticeIgnoreFlag�����Ρ�
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
	*/
	virtual void ES_CDECL OnRtnPositionProfit(const TAPISTR_20 UserNo, const TapAPIPositionProfitNotice *pRtnInfo) = 0;
	/**
	* @brief ��������ѯӦ��(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast ��ʾ�Ƿ������һ������
	* @param[in] pRspInfo ָ�򷵻ص����������Ϣ�ṹ�塣��nErrorCode��Ϊ0ʱ��pRspInfoΪ�ա�
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_DeepQuote
	*/
	virtual void ES_CDECL OnRspQryDeepQuote(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIDeepQuoteQryRsp *pRspInfo) = 0;
	/**
	* @brief ������ʱ��״̬��Ϣ֪ͨ(������ר��)
	* @param[out] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[out] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeSystem
	*/
	virtual void ES_CDECL OnRtnExchangeStateInfo(const TAPISTR_20 UserNo, const TapAPIExchangeStateInfoNotice *pRtnInfo) = 0;
	/**
	* @brief ѯ��֪ͨ(�����ǡ�������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
	*/
	virtual void ES_CDECL OnRtnReqQuoteNotice(const TAPISTR_20 UserNo, const TapAPIReqQuoteNotice *pRtnInfo) = 0;
	/**
	* @brief �ͻ����շ���Ӧ��(������ר��)
	* @details ��֤��������㷽ʽ������*ÿ�ֳ���*�������*�۸�
	*          ��֤�𶨶���㷽ʽ������*�������
	*          �����Ѿ��Է�ʽ���㷽ʽ������*�������������+����*ÿ�ֳ���*�۸�*�����������
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pRspInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_AccountRentInfo
	*/
	virtual void ES_CDECL OnRspAccountRentInfo(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIAccountRentInfo *pRspInfo) = 0;
	/**
	* @brief	������Ϣ��ѯӦ��
	* @details	�û����Բ�ѯ��صĽ�����Ϣ
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pRspInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeSystem
	*/
	virtual void ES_CDECL OnRspTradeMessage(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPITradeMessage *pRspInfo) = 0;
    /**
	* @brief	������Ϣ֪ͨ
	* @details	�û��ڽ��׹����п�����Ϊ�ʽ𡢳ֲ֡�ƽ�ֵ�״̬�䶯ʹ�˻�����ĳЩΣ��״̬������ĳЩ��Ҫ����Ϣ��Ҫ���û�֪ͨ��
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pRtnInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pRtnInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeSystem
	*/
	virtual void ES_CDECL OnRtnTradeMessage(const TAPISTR_20 UserNo, const TapAPITradeMessage *pRtnInfo) = 0;
	/**
	* @brief ��ʷί�в�ѯӦ��(�����ǡ���Ʊר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ĻỰID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo		ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_HisInfo
	*/
	virtual void ES_CDECL OnRspQryHisOrder(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIHisOrderQryRsp *pInfo) = 0;
	/**
	* @brief ��ʷί�����̲�ѯӦ��(�����ǡ���Ʊר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ĻỰID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo		ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_HisInfo
	*/
	virtual void ES_CDECL OnRspQryHisOrderProcess(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIHisOrderProcessQryRsp *pInfo) = 0;
	/**
	* @brief ��ʷ�ɽ���ѯӦ��(�����ǡ���Ʊר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ĻỰID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo		ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_HisInfo
	*/
	virtual void ES_CDECL OnRspQryHisFill(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIHisFillQryRsp *pInfo) = 0;
	/**
	* @brief ��ʷ�ֲֲ�ѯӦ��(�����ǡ���Ʊר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ĻỰID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo		ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_HisInfo
	*/
	virtual void ES_CDECL OnRspQryHisPosition(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIHisPositionQryRsp *pInfo) = 0;
	/**
	* @brief ��ʷ�����ѯӦ��(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ĻỰID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo		ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_HisInfo
	*/
	virtual void ES_CDECL OnRspQryHisDelivery(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIHisDeliveryQryRsp *pInfo) = 0;
	/**
	* @brief �ʽ������ѯӦ��(�����ǡ���Ʊר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ĻỰID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo		ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_FundInfo
	*/
	virtual void ES_CDECL OnRspQryAccountCashAdjust(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIAccountCashAdjustQryRsp *pInfo) = 0;
	/**
	* @brief ��ѯ�û��˵�Ӧ��
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ĻỰID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo		ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_Bill
	*/
	virtual void ES_CDECL OnRspQryBill(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIBillQryRsp *pInfo) = 0;
	/**
	* @brief ��ѯ�û������Ѳ���(�����ǡ���Ʊר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ĻỰID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo		ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_AccountRentInfo
	*/
	virtual void ES_CDECL OnRspAccountFeeRent(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIAccountFeeRentQryRsp *pInfo) = 0;
	/**
	* @brief ��ѯ�û���֤�����(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ĻỰID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo		ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_AccountRentInfo
	*/
	virtual void ES_CDECL OnRspAccountMarginRent(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIAccountMarginRentQryRsp *pInfo) = 0;
	/**
	* @brief ��¼�û��ֻ��豸����Ӧ��(�����ǡ���Ʊר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo		ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pInfo��ָʾ�����ݣ��������ý���������������Ч��
	* @operationtype �첽����
	*
	* @ingroup G_T_Cellphone
	*/
	virtual void ES_CDECL OnRspAddMobileDevice(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIMobileDeviceAddRsp *pInfo) = 0;
	/**
	* @brief ������־��ѯ(�����ǡ���Ʊר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo		ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pInfo��ָʾ�����ݣ��������ý���������������Ч��
	* @operationtype �첽����
	*
	* @ingroup G_T_Cellphone
	*/
	virtual void ES_CDECL OnRspQryManageInfoForEStar(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIManageInfo *pInfo) = 0;
	/**
	* @brief ϵͳ������ѯ(�����ǡ���Ʊר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo		ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pInfo��ָʾ�����ݣ��������ý���������������Ч��
	* @operationtype �첽����
	*
	* @ingroup G_T_Cellphone
	*/
	virtual void ES_CDECL OnRspQrySystemParameter(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPISystemParameterInfo *pInfo) = 0;
	/**
	* @brief ��������ǰ�õ�ַ��Ϣ��ѯ(�����ǡ���Ʊר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo		ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pInfo��ָʾ�����ݣ��������ý���������������Ч��
	* @operationtype �첽����
	*
	* @ingroup G_T_Cellphone
	*/
	virtual void ES_CDECL OnRspQryTradeCenterFrontAddress(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPITradeCenterFrontAddressInfo *pInfo) = 0;
	/**
	* @brief Ʒ����Ϣ֪ͨ(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_Commodity
	*/
	virtual void ES_CDECL OnRtnCommodityInfo(const TAPISTR_20 UserNo, const TapAPICommodityInfo *pInfo) = 0;
	/**
	* @brief ������Ϣ֪ͨ(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeSystem
	*/
	virtual void ES_CDECL OnRtnCurrencyInfo(const TAPISTR_20 UserNo, const TapAPICurrencyInfo *pInfo) = 0;
    /**
    * @brief �ͻ��ֻ�����ѯӦ��(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
    */
    virtual void ES_CDECL OnRspQryAccountStorage(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIAccountStorageInfo* pInfo) = 0;
    /**
    * @brief �ͻ��ֻ����֪ͨ(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
    */
    virtual void ES_CDECL OnRtnAccountStorage(const TAPISTR_20 UserNo, const TapAPIAccountStorageInfo* pInfo) = 0;
    /**
    * @brief �ͻ��ֻ���������ѯӦ��(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
    */
    virtual void ES_CDECL OnRspQrySpotLock(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPISpotLockInfo* pInfo) = 0;
    /**
    * @brief �ͻ��ֻ�������֪ͨ(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
    */
    virtual void ES_CDECL OnRtnSpotLock(const TAPISTR_20 UserNo, const TapAPISpotLockInfo* pInfo) = 0;
    /**
    * @brief	����ҵ��ί�в���Ӧ��(ETFר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
    * @details	����ҵ����������д�Ӧ��ص���sessionID��ʶ�����Ӧ��sessionID���Ա�ȷ���ñ�Ӧ���Ӧ������
    * @param[in] sessionID ����ĻỰID
    * @param[in] errorCode �����롣0 ��ʾ�ɹ�
    * @param[in] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
    * @attention ��Ҫ�޸ĺ�ɾ��pRtnInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
    * @ingroup G_T_ETF
    */
    virtual void ES_CDECL OnRspSpecialOrderAction(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, const TapAPISpecialOrderInfo *pRtnInfo) = 0;
    /**
    * @brief �ͻ�����ҵ��ί��֪ͨ(ETFר��)
 	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
    * @param[in] nRequestID ����ID
    * @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
    * @param[out] pInfo	ָ�򷵻ص���Ϣ�ṹ��
    * @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
    * @ingroup G_T_ETF
    */
    virtual void ES_CDECL OnRtnSpecialOrder(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPISpecialOrderInfo* pInfo) = 0;
    /**
    * @brief �ͻ���ϳֲ�֪ͨ(ETFר��)
	* @param[out] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[out] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_ETF
    */
    virtual void ES_CDECL OnRtnCombinePosition(const TAPISTR_20 UserNo, const TapAPICombinePositionInfo* pInfo) = 0;
    /**
    * @brief ���׺�Լ������Ϣ֪ͨ(�����ǡ���Ʊר��)
	* @param[out] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[out] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions 
    */
    virtual void ES_CDECL OnRtnContractQuote(const TAPISTR_20 UserNo, const TapAPIContractQuoteInfo* pInfo) = 0;
    /**
    * @brief �û������豸��ѯӦ��(�����ǡ���Ʊר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_UserInfo
    */
    virtual void ES_CDECL OnRspQryTrustDevice(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPITrustDeviceInfo* pInfo) = 0;
    /**
    * @brief �û������豸����Ӧ��(�����ǡ���Ʊר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_UserInfo
    */
    virtual void ES_CDECL OnRspAddTrustDevice(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPITrustDeviceAddRsp* pInfo) = 0;
    /**
    * @brief �û������豸ɾ��Ӧ��(�����ǡ���Ʊר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nRequestID ����ID
	* @param[in] nErrorCode �����롣0 ��ʾ�ɹ�
	* @param[in] isLast 	��ʾ�Ƿ������һ������
	* @param[in] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_UserInfo
    */
    virtual void ES_CDECL OnRspDelTrustDevice(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPITrustDeviceDelRsp* pInfo) = 0;
    /**
    * @brief �û�Ȩ������֪ͨ(������ר��)
	* @param[out] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[out] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_UserInfo 
    */
    virtual void ES_CDECL OnRtnAddUserRight(const TAPISTR_20 UserNo, const TapAPIUserRightInfo* pInfo) = 0;
    /**
    * @brief �û�Ȩ��ɾ��֪ͨ(������ר��)
	* @param[out] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[out] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_UserInfo 
    */
    virtual void ES_CDECL OnRtnDelUserRight(const TAPISTR_20 UserNo, const TapAPIUserRightInfo* pInfo) = 0;
    /**
    * @brief ��̨�����ļ���ѯӦ��ṹ(�����ǡ���Ʊר��)
    * @param[out] UserNo ָ�����Ϣ��Ӧ��UserNo
    * @param[out] nRequestID ����ID
    * @param[out] nErrorCode �����롣0 ��ʾ�ɹ�
    * @param[out] isLast ��ʾ�Ƿ������һ������
    * @param[out] pInfo ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
    * 
	* @ingroup G_T_TradeSystem
    */
    virtual void ES_CDECL OnRspQryManagerConfigFile(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIManagerConfigFileQryRsp* pInfo) = 0;
};

//EsTradeAPI ���⹦�ܽӿڡ��������û����Ե��õĹ��ܺ�����
class IEsTradeAPI
{
public:
	/**
	* @brief	����API�Ļص��ӿڶ���
	* @details	ϵͳ��API��֪ͨ��ͨ�����õĻص�����֪ͨ��ʹ���ߡ�
	*			IEsTradeAPINotify��API�Ļص��ӿڣ��û���Ҫ�̳�ʵ�ִ˽ӿ������������û���Ҫ�Ĺ��ܡ�
	*           ����û�û�����ûص��ӿڣ���API�������û������κ����õ���Ϣ��
	* @param[in] pApiNotify ʵ����IEsTradeAPINotify�ӿڵĶ���ָ��
	* @operationtype ͬ������
	* 
	* @ingroup G_T_Login
	*/
	virtual TAPIINT32 ES_CDECL SetAPINotify(IEsTradeAPINotify *pApiNotify) = 0;
	/**
	* @brief	����API����������Ŀ¼
	* @details	���ú�����ͬʱ����path������Ŀ¼�´����������գ���ʽEsTradeAPIYYYYMMDD.log)�������ļ���
	*			�ļ��б��������ΪAPI���յ�����Ҫ���ݺ�API��ʹ�úʹ�����־��
	* @param[in] pPath Ŀ¼��������ã�Ŀ¼����Window��Ϊ��\\�����ߡ�/��, Linux��Ϊ��/��
	* @retval 0 ���óɹ�����0 ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_LogConfig
	*/
	virtual TAPIINT32 ES_CDECL SetEsTradeAPIDataPath(const TAPICHAR *pPath) = 0;
	/**
	* @brief	����API����־����
	* @details	�趨��־���������ֻ�е�ʵ����־������˴��趨�ļ�����ͬ�����ʱ���ŻὫ��־д��SetEsTradeAPIDataPath()�����򿪵���־�ļ���
	*			Ĭ����־����ΪAPILOGLEVEL_ERROR��
	* @param[in] LogLevel ��־����
	*			APILOGLEVEL_ERROR	��ֻ��¼Error��־
	*			APILOGLEVEL_NORMAL	����¼Error��־����ͨ��־
	*			APILOGLEVEL_DEBUG	����¼Error��־��Debug��־
	* @retval 0 �趨�ɹ�����0 ������
	* @operationtype ͬ������
	* @remark ��API����һ������EsTradeAPIYYYYMMDD.log��־�ļ��м�¼һЩAPI��Ϊ����Ҫ��¼����־��
    * 
	* @ingroup G_T_LogConfig
	*/
	virtual TAPIINT32 ES_CDECL SetEsTradeAPILogLevel(TAPILOGLEVEL LogLevel) = 0;
	/**
	* @brief		���õ�¼�û���Ϣ��API֧�ֶ��½�����Զ�ε��øýӿڡ�
	* @param[in]	pUserInfo ��¼�û���Ϣ
	* @retval		0 ���óɹ�����0 ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_Login
	*/
	virtual TAPIINT32 ES_CDECL SetUserInfo(const TapAPITradeUserInfo *pUserInfo) = 0;
    /**
     * @brief ���ñ��õ�¼��ַ(������ר��)
     * @param pAddress ��¼��ַ
     * @return 0 ���óɹ�����0 ������
     * 
     * @ingroup G_T_Login
     */
    virtual TAPIINT32 ES_CDECL SetBackUpAddress(const TAPISTR_20 UserNo, const TapAPIBackUpAddress *pAddress) = 0;
    /**
     * @brief �����֤����(�����ǣ���Ʊר��)
     * @details ���ͻ���������ʱ�����������������룬��һ������Ҫ���������֤��
     * @param UserNo �����֤�û�
     * @param pIdentity ��֤��Ϣ
     * @return 0 ���óɹ�����0 ������
     * 
     * @ingroup G_T_Login
     */
    virtual TAPIINT32 ES_CDECL RequestVerifyIdentity(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, const TapAPIVerifyIdentity *pIdentity) = 0;
	/**
	* @brief	����ĳһ���û�����ʼ������API�ڲ������ӷ��񣬽�����·�������¼��֤��ά����·��Ϣ��
	*			���������·�Ͽ���API�ڲ����Զ������������������ɹ����ٴ��Զ������¼��֤��
	*			������ֵ�¼ʧ�ܣ�API�ڲ���ֹͣ�ظ���¼������������󣩣���ʱ��ҪAPIʹ�����ȵ���StopUser��Ȼ���ٴ�ʹ����ȷ�ĵ�¼��Ϣ����StartUser
	* @details	��ʹ�ú���ǰ�û���Ҫ��ɵ�¼�û���Ϣ������SetUserInfo()�����Ҵ���EsTdAPITradeLoginAuth���͵��û���Ϣ��
	*			������Ҫ���úûص��ӿڡ�
	*			��¼�����н������ӵķ�����Ϣͨ���ص�OnConnect���ظ��û���
	*			���ӽ�������û���֤������Ϣͨ���ص�OnLogin()���ظ��û���
	*			��¼�ɹ���API���Զ�����API�ĳ�ʼ����API�����������������ݣ���ѯ���Ժ��ͨ���ص�OnAPIReady()
	*			ָʾ�û�API��ʼ����ɣ����Խ��к����Ĳ����ˡ�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] pLoginAuth ��¼��֤��Ϣ�ṹָ�롣������¼��Ҫ����֤��Ϣ
	* @retval 0 ��¼�ɹ���API��ʼ׼����̨����;��0 ������
	* @operationtype �첽����
	* @note EsTdAPITradeLoginAuth�е�NoticeIgnoreFlag���ڱ���Ƿ�����ض���֪ͨ�ص���
	*       ���磺����Ҫ����OnRtnFund��OnRtnPositionProfit,������ô�趨��
	*       NoticeIgnoreFlag = TAPI_NOTICE_IGNORE_FUND | TAPI_NOTICE_IGNORE_POSITIONPROFIT;
	* 
	* @ingroup G_T_Login
	*/
	virtual TAPIINT32 ES_CDECL StartUser(const TAPISTR_20 UserNo, const TapAPITradeLoginAuth *pLoginAuth) = 0;
	/**
	* @brief ֹͣĳһ���û���API���û��˳����Ͽ����ӣ�ֹͣ������
	* @details ���ú�����API���ǳ����Ͽ�������������ӡ�
	* @param[in] UserNo ��¼�û�UserNo
	* @operationtype ͬ������
	* 
	* @ingroup G_T_Disconnect
	*/
	virtual TAPIINT32 ES_CDECL StopUser(const TAPISTR_20 UserNo) = 0;
	/**
	* @brief	�����Ͷ�����֤��֤��(�����ǣ���Ʊר��)
	* @details	���ݻص�����OnRtnContactInfo�е���ϵ��ʽ��ѡ������һ�����������֤�룬
	*			�յ���ȷӦ������ͨ��SetVertificateCode ���ö�����֤��Ȩ����ɵ�½���̡�
	* @param[in]	UserNo ��¼�û�UserNo
	* @param[in] nSessionID ��������ĻỰID
	* @param[in]  pReqInfo Ҫ���ն�����֤��������ߵ绰
	* @attention �ú���������Ҫ�ڵ�½Ӧ��󷵻�10003����API��ص��ͻ�������֤����ϵ��ʽ���û�ѡ������һ����ϵ��ʽ��������ߵ绰�����������֤��
	*    ��ͨ�����ö�����֤��Ȩ����ɵ�½��
	* 
	* @ingroup G_T_Login
	*/
	virtual TAPIINT32 ES_CDECL RequestVertificateCode(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, const TapAPISecondInfo *pReqInfo) = 0;
	/**
	* @brief	���ö�����֤��Ϣ��(�����ǣ���Ʊר��)
	* @details	��¼��ɺ����ϵͳ������Ҫ���ж�����֤�����룬���¼�����ʾ��Ҫ���ж�����֤��
	*			��ʱ���øú������������֤����ɵ�¼��
	*			��¼��ɺ������ٵ��ô˺���������ԭ������ĵ�¼ʧ��Ҳ���ܵ��ô˺���������᷵�ض�Ӧ�Ĵ�����Ϣ��
	*			���ô˽ӿں󣬻᷵�ص�¼Ӧ��ɹ����ı�ǣ�����ɹ���ʾ��¼��ɣ����Եȴ�OnAPIReady API��ɻص���
	*			�����ʱ���ص���ɺ�API�������Ͽ����ӣ���Ҫ�ٴν��е�¼������
	*			�����֤�����������ٴε��ô˺���������ȷ����֤�������֤��
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nSessionID ��������ĻỰID
	* @param[in] VertificateCode ������֤��
	* @retval 0 ������֤��ɹ�
	* @retval ��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_Login
	*/
	virtual TAPIINT32 ES_CDECL SetVertificateCode(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, const TapAPISecondCertificationReq *pReqInfo) = 0;
	/**
	* @brief �м��û��ύ�û���¼��Ϣ(������ר��)
	* @details ��¼�ɹ���ֻ���м��û�����ʹ�øú���
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID �˴��ύ�û���¼��Ϣ������ID
	* @param[in] pUserLoginInfo �û���¼��Ϣ
	* @retval 0 �ɹ�����0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_UserInfo
	*/
	virtual TAPIINT32 ES_CDECL SubmitUserLoginInfo(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPISubmitUserLoginInfo* pUserLoginInfo) = 0;
	/**
	* @brief �޸�����
	* @details �ɹ����û����뽫�����ó�newPassword
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID �˴��޸����������ID
	* @param[in] pReqInfo �����޸�����Ľṹ��ָ��
	* @retval 0 �ɹ�����0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_UserInfo
	*/
	virtual TAPIINT32 ES_CDECL ChangePassword(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIChangePasswordReq *pReqInfo) = 0;
	/**
	* @brief ��ȡ��¼�û��Ƿ����ĳȨ��
	* @details �û���Ȩ�����û���¼ʱ�Ѿ����ݸ�API�����Դ˺���ִ�е��Ǳ��صĲ�ѯ��
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRightID Ȩ��ID
	* @retval 0 ������Ȩ�ޣ� ��0 ����Ȩ��
	* @operationtype ͬ������
	* 
	* @ingroup G_T_UserRight
	*/
	virtual TAPIINT32 ES_CDECL HaveCertainRight(const TAPISTR_20 UserNo, TAPIRightIDType nRightID) = 0;
	/**
	* @brief �����û�Ԥ����Ϣ
	* @details �û���������һ������Ϊ50���ڵ��ַ���Ϣ���´ε�¼����Եõ������Ϣ�����������Ҫ���������û�ȷ�����Լ����˺ţ���Ҫ���������з�α��
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] info Ԥ����Ϣ�ַ���ָ��
	* @retval 0 ����ɹ�����0 ������
	* @operationtype �첽����
	* @note �ýӿ���δʵ��
	* 
	* @ingroup G_T_UserInfo
	*/
	virtual TAPIINT32 ES_CDECL SetReservedInfo(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TAPISTR_50 info) = 0;
	/**
	* @brief ��ȡ�û������������ʽ��˺š���SeqID��ʼ��ѯ��ÿ����෵��nOutLen�������û�н�������Ҫ�´μ����Ӳ�ѯ�������һ�����ݵ�SeqID+1������ѯ��
	* @details �˺���ִ�е��Ǳ��صĲ�ѯ,�����в���ɾ���Ѿ��Ӻ�̨��ȡ�����ʽ��˺���Ϣ
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nDataSeqID ��ʼ��ѯ���ݱ�ţ�1��ʾ��һ�����ݣ����β�ѯ���������ŵ����ݣ�
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_AccountInfo
	*/
	virtual TAPIINT32 ES_CDECL GetAccount(const TAPISTR_20 UserNo, TAPIUINT32 nDataSeqID, TapAPIAccountInfo* pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
	/**
	* @brief ��ȡָ���û��µ����н�������Ϣ����SeqID��ʼ��ÿ����෵��nOutLen�������û�н�������Ҫ�´μ����Ӳ�ѯ�������һ�����ݵ�SeqID+1������ѯ��
	* @details �˺���ִ�е��Ǳ��صĲ�ѯ,�����в���ɾ���Ѿ��Ӻ�̨��ȡ���Ľ�������Ϣ
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nDataSeqID ��ʼ��ѯ���ݱ�ţ�1��ʾ��һ�����ݣ����β�ѯ���������ŵ����ݣ�
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������(Synchronous operation)
	* 
	* @ingroup G_T_TradeSystem
	*/
	virtual TAPIINT32 ES_CDECL GetExchange(const TAPISTR_20 UserNo, TAPIUINT32 nDataSeqID, TapAPIExchangeInfo* pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
	/**
	* @brief ��ȡָ���û��µ�����Ʒ����Ϣ����SeqID��ʼ��ÿ����෵��nOutLen�������û�н�������Ҫ�´μ����Ӳ�ѯ�������һ�����ݵ�SeqID+1������ѯ��
	* @details �˺���ִ�е��Ǳ��صĲ�ѯ,�����в���ɾ���Ѿ��Ӻ�̨��ȡ����Ʒ����Ϣ
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nDataSeqID ��ʼ��ѯ���ݱ�ţ�1��ʾ��һ�����ݣ����β�ѯ���������ŵ����ݣ�
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_Commodity
	*/
	virtual TAPIINT32 ES_CDECL GetCommodity(const TAPISTR_20 UserNo, TAPIUINT32 nDataSeqID, TapAPICommodityInfo* pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
	/**
	* @brief ��ȡָ���û��µ�ָ��Ʒ�ֵĺ�Լ��Ϣ����SeqID��ʼ��ѯ��ÿ����෵��nOutLen�������û�н�������Ҫ�´μ����Ӳ�ѯ�������һ�����ݵ�SeqID+1������ѯ��(�����ǡ�������)
	* @details �˺���ִ�е��Ǳ��صĲ�ѯ,�����в���ɾ���Ѿ��Ӻ�̨��ȡ���ĺ�Լ��Ϣ
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] pReqInfo ��ѯ�û���ָ��Ʒ�ֵĺ�Լ��Ϣ����Ľṹ��ָ��
	*    �ò������ֶ�Ϊ��ѡ�ֶΣ����������·�����ѯ��
	*    1.������Ϊ�գ������к�Լ
	*    2.������������Ч��Ʒ�ֱ���Ϊ�գ���ý����������еĺ�Լ
	*    3.������������Ч��Ʒ�ֱ�����Ч����ý�������ָ��Ʒ�ֵ����к�Լ
	*    4.������������Ч��Ʒ�ֱ�����Ч��Ʒ��������Ч�����Ʒ����ָ��Ʒ�����͵����к�Լ
	* @param[in] nDataSeqID ��ʼ��ѯ���ݱ�ţ�1��ʾ��һ�����ݣ����β�ѯ���������ŵ����ݣ�
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_Contract
	*/
	virtual TAPIINT32 ES_CDECL GetContract(const TAPISTR_20 UserNo, const TapAPICommodity *pReqInfo, TAPIUINT32 nDataSeqID, TapAPITradeContractInfo* pOutInfo[], TAPIUINT32 nOutLen,  TAPIYNFLAG& isLast) = 0;
	/**
	* @brief �µ�
	* @details �û��µ��Ĳ����������û����µ�����������û����ʽ𡢳ֲ֡�ƽ�֡��ʽ𡢷�ر�ǵȶ������ݵı仯�������û��µĵ��ɽ��󣬻��ж���ص�֪ͨ�����û�չʾ���ݵı仯��
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pOrder �µ�ί��
	* @retval 0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_TradeActions
	*/
	virtual TAPIINT32 ES_CDECL InsertOrder(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPINewOrder *pOrder) = 0;
	/**
	* @brief ����
	* @details �û�ί��û����ȫ�ɽ�֮ǰ����ʣ���ί��
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pOrder ������ί��
	* @retval 0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_TradeActions
	*/
	virtual TAPIINT32 ES_CDECL CancelOrder(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIOrderCancelReq *pOrder) = 0;
	/**
	* @brief �����޸�ָ��(�����ǡ���Ʊר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pOrder �����޸�����ṹ
	* @retval 0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_TradeActions
	*/
	virtual TAPIINT32 ES_CDECL ModifyOrder(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIOrderModifyReq *pOrder) = 0;
	/**
	* @brief �����
	* @details �������ı�����ί�н��������¿�ʼ�����ɽ�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pOrder �����ί��
	* @retval 0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_TradeActions
	*/
	virtual TAPIINT32 ES_CDECL ActivateOrder(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIOrderActivateReq *pOrder) = 0;
	/**
	* @brief ��ȡָ���û���ָ���ʽ��˻��ĵ�ǰ�����ʽ���Ϣ
	* @details TapAPIFundReq��Ҫ��д�ʽ��˺š�TapAPIFundReq����Ҫ��д��ѯ���ݵ���ʼ���š�
	* @details �˺�����ѯ���Ǳ��صĲ�ѯ,�����в���ɾ���Ѿ��Ӻ�̨��ȡ�����ʽ��˺��µ��ʽ����ݡ�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] pReqInfo ��ѯ�ͻ��ʽ�����Ľṹ��ָ��
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_FundInfo
	*/
	virtual TAPIINT32 ES_CDECL GetFund(const TAPISTR_20 UserNo, const TapAPIFundReq *pReqInfo, TapAPIFundData* pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
	/**
	* @brief ��ȡָ���û���ָ�������ĵ�ǰ����ί����Ϣ�����Բ�ѯ����ί�У�Ҳ���Բ�ѯ����δ������ί�С�
	* @details �˺�����ѯ���Ǳ��صĲ�ѯ,�û��ͺ�̨�Ͽ����������ձ������ݡ�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] pReqInfo ��ѯ�ͻ�ί������Ľṹ��ָ��
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_TradeInfo
	*/
	virtual TAPIINT32 ES_CDECL GetOrder(const TAPISTR_20 UserNo, const TapAPIOrderQryReq *pReqInfo, TapAPIOrderInfo pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
	/**
	* @brief ��ѯί�б仯����
	* @details ��ѯ�û���ί�еı仯���̣���ѯ������ί�е�ÿһ�εı仯��
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pReqInfo ί�����̲�ѯ��Ϣ�ṹ��ָ��
	* @retval 0 ����ɹ�����0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_TradeInfo
	*/
	virtual TAPIINT32 ES_CDECL QryOrderProcess(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIOrderProcessQryReq *pReqInfo) = 0;
	/**
	* @brief ��ȡָ���û���ָ�������ĳɽ���Ϣ
	* @details �˺�����ѯ���Ǳ��صĲ�ѯ,�û��ͺ�̨�Ͽ����������ձ������ݡ�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] pReqInfo ��ѯ�ͻ�ί������Ľṹ��ָ��
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_TradeInfo
	*/
	virtual TAPIINT32 ES_CDECL GetFill(const TAPISTR_20 UserNo, const TapAPIFillQryReq *pReqInfo, TapAPIFillInfo pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
	/**
	* @brief ��ȡָ���û���ָ�������ĳֲ���Ϣ
	* @details �˺�����ѯ���Ǳ��صĲ�ѯ,�û��ͺ�̨�Ͽ����������ձ������ݡ�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] pReqInfo ��ѯ�ͻ�ί������Ľṹ��ָ��
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_TradeInfo
	*/
	virtual TAPIINT32 ES_CDECL GetPosition(const TAPISTR_20 UserNo, const TapAPIPositionQryReq *pReqInfo, TapAPIPositionInfo pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
	/**
	* @brief ��ȡָ���û���ָ�������ĳֲֻ�����Ϣ
	* @details �˺�����ѯ���Ǳ��صĲ�ѯ,�û��ͺ�̨�Ͽ����������ձ������ݡ�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] pReqInfo ��ѯ�ͻ�ί������Ľṹ��ָ��
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_TradeInfo
	*/
	virtual TAPIINT32 ES_CDECL GetPositionSum(const TAPISTR_20 UserNo, const TapAPIPositionQryReq *pReqInfo, TapAPIPositionSumInfo pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
	/**
	* @brief ��ȡָ���û���ָ��������ƽ�ּ�¼(������ר��)
	* @details �˺�����ѯ���Ǳ��صĲ�ѯ,�û��ͺ�̨�Ͽ����������ձ������ݡ�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] pReqInfo ��ѯ�ͻ�ί������Ľṹ��ָ��
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_TradeInfo
	*/
	virtual TAPIINT32 ES_CDECL GetClose(const TAPISTR_20 UserNo, const TapAPICloseQryReq *pReqInfo, TapAPICloseInfo pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
	/**
	* @brief ��ѯ�������(������ר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pReqInfo ��ѯ������������ṹ��ָ��
	* @retval 0 ����ɹ�����0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_DeepQuote
	*/
	virtual TAPIINT32 ES_CDECL QryDeepQuote(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIContract *pReqInfo) = 0;
	/**
	* @brief ��ȡָ���û��µĽ�����ʱ��״̬��Ϣ(������)����SeqID��ʼ��ÿ����෵��nOutLen�������û�н�������Ҫ�´μ����Ӳ�ѯ�������һ�����ݵ�SeqID+1������ѯ��
	* @details �˺���ִ�е��Ǳ��صĲ�ѯ,�����в���ɾ���Ѿ��Ӻ�̨��ȡ���Ľ�������Ϣ
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nDataSeqID ��ʼ��ѯ���ݱ�ţ�1��ʾ��һ�����ݣ����β�ѯ���������ŵ����ݣ�
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_TradeSystem
	*/
	virtual TAPIINT32 ES_CDECL GetExchangeStateInfo(const TAPISTR_20 UserNo, TAPIUINT32 nDataSeqID, TapAPIExchangeStateInfo* pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
	/**
	* @brief ��ȡָ���û��µ�������Ϣ,��Ҫ�����ڿͻ��µ�ʱָ��ͨ���ţ���������ѡ���ӽ��뽻����ǰ�û�(������ר��)
	* @details �˺���ִ�е��Ǳ��صĲ�ѯ,�����в���ɾ���Ѿ��Ӻ�̨��ȡ��������ͨ����Ϣ
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nDataSeqID ��ʼ��ѯ���ݱ�ţ�1��ʾ��һ�����ݣ����β�ѯ���������ŵ����ݣ�
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_UpperChannelInfo
	*/
	virtual TAPIINT32 ES_CDECL GetUpperChannel(const TAPISTR_20 UserNo, TAPIUINT32 nDataSeqID, TapAPIUpperChannelInfo* pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
	/**
	* @brief ��ȡָ���û������еı��ֵ���Ϣ����SeqID��ʼ��ѯ��ÿ����෵��100�������û�н�������Ҫ�´μ����Ӳ�ѯ�������һ�����ݵ�SeqID������ѯ�������ǡ���Ʊר�ã�
	* @details �˺���ִ�е��Ǳ��صĲ�ѯ,�����в���ɾ���Ѿ��Ӻ�̨��ȡ���ı�����Ϣ����
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nDataSeqID ��ʼ��ѯ���ݱ�ţ�1��ʾ��һ�����ݣ����β�ѯ���������ŵ����ݣ�
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_TradeSystem
	*/
	virtual TAPIINT32 ES_CDECL GetCurrency(const TAPISTR_20 UserNo, TAPIUINT32 nDataSeqID, TapAPICurrencyInfo* pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
	/**
	* @brief ��ѯ�ͻ����շ��ʣ�������ר�ã�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pReqInfo �ͻ����շ��ʲ�ѯ����ṹ��ָ��
	* @retval 0 ����ɹ�����0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_AccountRentInfo
	*/
	virtual TAPIINT32 ES_CDECL QryAccountRent(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIAccountRentQryReq *pReqInfo) = 0;
	/**
	* @brief ��ѯ�ͻ������Ѳ����������ǡ���Ʊר�ã�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pReqInfo �ͻ����շ��ʲ�ѯ����ṹ��ָ��
	* @retval 0 ����ɹ�����0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_AccountRentInfo
	*/
	virtual TAPIINT32 ES_CDECL QryAccountFeeRent(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIAccountFeeRentQryReq *pReqInfo) = 0;
	/**
	* @brief ��ѯ�ͻ���֤�������������ר�ã�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pReqInfo �ͻ����շ��ʲ�ѯ����ṹ��ָ��
	* @retval 0 ����ɹ�����0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_AccountRentInfo
	*/
	virtual TAPIINT32 ES_CDECL QryAccountMarginRent(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIAccountMarginRentQryReq *pReqInfo) = 0;
	/**
	* @brief �ͻ��ʽ������ѯ����(�����ǡ���Ʊר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pReqInfo �ͻ��ʽ������ѯ����ṹ��ָ��
	* @retval 0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_FundInfo
	*/
	virtual TAPIINT32 ES_CDECL QryAccountCashAdjust(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIAccountCashAdjustQryReq *pReqInfo) = 0;
	/**
	* @brief ��ѯ�û��˵�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pReqInfo �ͻ��û��˵���ѯ����ṹ��ָ��
	* @retval 0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_Bill
	*/
	virtual TAPIINT32 ES_CDECL QryBill(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIBillQryReq *pReqInfo) = 0;
	/**
	* @brief ��ʷί�в�ѯ����(�����ǡ���Ʊר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pReqInfo �ͻ���ʷί�в�ѯ����ṹ��ָ��
	* @retval 0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_HisInfo
	*/
	virtual TAPIINT32 ES_CDECL QryHisOrder(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIHisOrderQryReq *pReqInfo) = 0;
	/**
	* @brief ��ʷί�����̲�ѯ����(�����ǡ���Ʊר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pReqInfo �ͻ���ʷί�����̲�ѯ����ṹ��ָ��
	* @retval 0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_HisInfo
	*/
	virtual TAPIINT32 ES_CDECL QryHisOrderProcess(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIHisOrderProcessQryReq *pReqInfo) = 0;
	/**
	* @brief ��ʷ�ɽ���ѯ����(�����ǡ���Ʊר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pReqInfo �ͻ���ʷ�ɽ���ѯ����ṹ��ָ��
	* @retval 0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_HisInfo
	*/
	virtual TAPIINT32 ES_CDECL QryHisFill(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIHisFillQryReq *pReqInfo) = 0;
	/**
	* @brief ��ʷ�ֲֲ�ѯ����(�����ǡ���Ʊר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pReqInfo �ͻ���ʷ�ֲֲ�ѯ����ṹ��ָ��
	* @retval 0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_HisInfo
	*/
	virtual TAPIINT32 ES_CDECL QryHisPosition(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIHisPositionQryReq *pReqInfo) = 0;
	/**
	* @brief ��ʷ�����ѯ����(������ר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pReqInfo �ͻ���ʷ�����ѯ����ṹ��ָ��
	* @retval 0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_HisInfo
	*/
	virtual TAPIINT32 ES_CDECL QryHisDelivery(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIHisDeliveryQryReq *pReqInfo) = 0;
	/**
	* @brief ��¼�û��ֻ��豸����(�����ǡ���Ʊר��)
	* @param[in]	UserNo ��¼�û�UserNo
	* @param[in]	nRequestID ����ID
	* @param[in]	pReqInfo ��¼�û��ֻ��豸��������ṹ
	* @retval		0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_Cellphone
	*/
	virtual TAPIINT32 ES_CDECL AddMobileDevice(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIMobileDeviceAddReq *pReqInfo) = 0;
	/**
	* @brief ������־��ѯ(�����ǡ���Ʊר��)
	* @param[in]	UserNo ��¼�û�UserNo
	* @param[in]	nRequestID ����ID
	* @param[in]	pReqInfo ������־��ѯ����ṹ
	* @retval		0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_Cellphone
	*/
	virtual TAPIINT32 ES_CDECL QryManageInfoForEStar(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIManageInfoQryReq *pReqInfo) = 0;
	/**
	* @brief ϵͳ������ѯ(�����ǡ���Ʊר��)
	* @param[in]	UserNo ��¼�û�UserNo
	* @param[in]	nRequestID ����ID
	* @param[in]	pReqInfo ϵͳ������ѯ����ṹ
	* @retval		0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_Cellphone
	*/
	virtual TAPIINT32 ES_CDECL QrySystemParameter(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPISystemParameterQryReq *pReqInfo) = 0;
	/**
	* @brief ��������ǰ�õ�ַ��Ϣ��ѯ(�����ǡ���Ʊר��)
	* @param[in]	UserNo ��¼�û�UserNo
	* @param[in]	nRequestID ����ID
	* @param[in]	pReqInfo ��������ǰ�õ�ַ��Ϣ��ѯ����ṹ
	* @retval		0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_Cellphone
	*/
	virtual TAPIINT32 ES_CDECL QryTradeCenterFrontAddress(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPITradeCenterFrontAddressQryReq *pReqInfo) = 0;
    /**
	* @brief ������Ϣ��ѯ
	* @param[in]	UserNo ��¼�û�UserNo
	* @param[in]	nRequestID ����ID
	* @param[in]	pReqInfo ������Ϣ��ѯ����ṹ
	* @retval		0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_TradeSystem
	*/
    virtual TAPIINT32 ES_CDECL QryTradeMessage(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPITradeMessageQryReq *pReqInfo) = 0;
    /**
	* @brief �ͻ��ֻ�����ѯ(������ר��)
	* @param[in]	UserNo ��¼�û�UserNo
	* @param[in]	nRequestID ����ID
	* @param[in]	pReqInfo �ͻ��ֻ�����ѯ����ṹ
	* @retval		0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_TradeActions
	*/
    virtual TAPIINT32 ES_CDECL QryAccountStorage(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIAccountStorageQryReq *pReqInfo) = 0;
    /**
	* @brief �ͻ��ֻ���������ѯ(������ר��)
	* @param[in]	UserNo ��¼�û�UserNo
	* @param[in]	nRequestID ����ID
	* @param[in]	pReqInfo �ͻ��ֻ�����ѯ����ṹ
	* @retval		0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_TradeActions
	*/
    virtual TAPIINT32 ES_CDECL QrySpotLock(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPISpotLockQryReq* pReqInfo) = 0;
    /**
	* @brief �ͻ�����ҵ��ί���µ�(ETFר��)
	* @details �û��µ��Ĳ����������û����µ�����������û����ʽ���ϳֲ����ݵı仯�������û��µĵ��ɽ��󣬻��ж���ص�֪ͨ�����û�չʾ���ݵı仯��
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] pOrder �µ�ί��
	* @retval 0 ����ɹ�;��0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_ETF
	*/
	virtual TAPIINT32 ES_CDECL InsertSpecialOrder(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPISpecialOrderInsertReq *pOrder) = 0;
    /**
	* @brief ��ȡָ���û���ָ�������ĵ�ǰ����ί����Ϣ��(ETFר��)
	* @details �˺�����ѯ���Ǳ��صĲ�ѯ,�û��ͺ�̨�Ͽ����������ձ������ݡ�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] pReqInfo ��ѯ�ͻ�ί������Ľṹ��ָ��
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_ETF
	*/
	virtual TAPIINT32 ES_CDECL GetSpecialOrder(const TAPISTR_20 UserNo, const TapAPISpecialOrderQryReq *pReqInfo, TapAPISpecialOrderInfo pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
	/**
	* @brief ��ȡָ���û���ָ�������ĳֲ���Ϣ(ETFר��)
	* @details �˺�����ѯ���Ǳ��صĲ�ѯ,�û��ͺ�̨�Ͽ����������ձ������ݡ�
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] pReqInfo ��ѯ�ͻ�ί������Ľṹ��ָ��
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_ETF
	*/
	virtual TAPIINT32 ES_CDECL GetCombinePosition(const TAPISTR_20 UserNo, const TapAPICombinePositionQryReq *pReqInfo, TapAPICombinePositionInfo pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
    /**
	* @brief ��ѯ�û������豸��Ϣ(�����ǡ���Ʊר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] info �û������豸��ѯ����ṹ��
	* @retval 0 ����ɹ�����0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_UserInfo
	*/
    virtual TAPIINT32 ES_CDECL QryTrustDevice(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPITrustDeviceQryReq* pReqInfo) = 0;
    /**
	* @brief �����û������豸��Ϣ(�����ǡ���Ʊר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] info �û������豸��������ṹ��
	* @retval 0 ����ɹ�����0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_UserInfo
	*/
    virtual TAPIINT32 ES_CDECL AddTrustDevice(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPITrustDeviceAddReq* pReqInfo) = 0;
    /**
	* @brief ɾ���û������豸��Ϣ(�����ǡ���Ʊר��)
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nRequestID ����ID
	* @param[in] info �û������豸ɾ������ṹ��
	* @retval 0 ����ɹ�����0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_UserInfo
	*/
    virtual TAPIINT32 ES_CDECL DelTrustDevice(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPITrustDeviceDelReq* pReqInfo) = 0;
    /**
	* @brief ��ȡ������С�䶯�ۡ�����Ʊ��̨ר�ã�
	* @details �˺���ִ�е��Ǳ��صĲ�ѯ,�����в���ɾ���Ѿ��Ӻ�̨��ȡ������Ϣ����
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nDataSeqID ��ʼ��ѯ���ݱ�ţ�1��ʾ��һ�����ݣ����β�ѯ���������ŵ����ݣ�
	* @param[in] pOutInfo ���β�ѯӦ����Ϣָ���������ʼ��ַ
	* @param[in] nOutLen ���β�ѯӦ����Ϣָ������ĳ���
	* @param[out] isLast ��ʾ���㱾�β�ѯ��Ӧ����Ϣ�Ƿ�������
	* @retval retval>=0 ���β�ѯ���ķ���������Ӧ����Ϣ���ܸ�����retval������Ϊ����ʱ��һ������; retval<0 ���β�ѯʧ�ܣ���ʾ������
	* @operationtype ͬ������
	* 
	* @ingroup G_T_TradeSystem
	*/
	virtual TAPIINT32 ES_CDECL GetStepTickSize(const TAPISTR_20 UserNo, TAPIUINT32 nDataSeqID, TapAPIStepTickSize* pOutInfo[], TAPIUINT32 nOutLen, TAPIYNFLAG& isLast) = 0;
    /**
    * ��ѯ��̨�����ļ�(�����ǡ���Ʊ��̨ר��)
    * @param[in] UserNo ��¼�û�UserNo
    * @param[in] nRequestID ����ID
    * @param[in] pReqInfo ��̨�����ļ���ѯ����ṹ
    * @retval 0 ����ɹ�����0 ������
	* @operationtype �첽����
	* 
	* @ingroup G_T_TradeSystem
    */
    virtual TAPIINT32 ES_CDECL QryManagerConfigFile(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIManagerConfigFileQryReq* pReqInfo) = 0;
};

}

//-----------------------------EsTradeAPI��������------------------------------------
#ifdef __cplusplus
extern "C" {
#endif // __cplusplus
/**
* @brief	����EsTradeAPI�Ľӿڶ���
* @details	������������API�Ľӿ�
* @param[in] nResult �����ӿڵĴ�����
* @retval NULL ����ʧ�ܣ�����ԭ���ͨ���������nResult�ж�
* @retval !NULL	ʵ����IEsTradeAPI�ӿڵĶ���ָ��
* 
* @ingroup G_T_API
*/
ES_DLLEXPORT EsTradeAPI::IEsTradeAPI *ES_CDECL CreateEsTradeAPI(EsTradeAPI::TAPIINT32& nResult);
/**
* @brief	����ͨ��CreateEsTradeAPI����������IEsTradeAPI����
* @param[in] pApiObj IEsTradeAPI����ָ��
* 
* @ingroup G_T_API
*/
ES_DLLEXPORT void ES_CDECL FreeEsTradeAPI(EsTradeAPI::IEsTradeAPI *pApiObj);
/**
* @brief	��ȡEsTradeAPI�İ汾��Ϣ
* @param[out] pVersion �ⲿ�����ַ����飬����API�汾��
* @param[in] nVersionLen �ַ����鳤�ȣ�������50���ַ�
* 
* @ingroup G_T_API
*/
ES_DLLEXPORT void ES_CDECL GetEsTradeAPIVersion(char* pVersion, int nVersionLen);
#ifdef __cplusplus
}
#endif // __cplusplus

#endif // ES_TRADE_API_H
