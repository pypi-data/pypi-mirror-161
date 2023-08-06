//ϵͳ
#ifdef WIN32
#include "stdafx.h"
#endif

#include "vnesunny.h"
#include "pybind11/pybind11.h"
#include "esunny/EsTradeAPI.h"
#include "esunny/TapDataCollectAPI.h"


using namespace pybind11;
using namespace EsTradeAPI;

//����
#define ONCONNECT 0
#define ONRSPLOGIN 1
#define ONRTNCONTACTINFO 2
#define ONRSPREQUESTVERTIFICATECODE 3
#define ONRSPREQUESTVERIFYIDENTITY 4
#define ONRSPSETVERTIFICATECODE 5
#define ONRTNERRORMSG 6
#define ONAPIREADY 7
#define ONDISCONNECT 8
#define ONRSPSUBMITUSERLOGININFO 9
#define ONRSPCHANGEPASSWORD 10
#define ONRSPSETRESERVEDINFO 11
#define ONRTNCONTRACT 12
#define ONRTNFUND 13
#define ONRTNORDER 14
#define ONRSPORDERACTION 15
#define ONRSPQRYORDERPROCESS 16
#define ONRTNFILL 17
#define ONRTNPOSITION 18
#define ONRTNCLOSE 19
#define ONRTNPOSITIONPROFIT 20
#define ONRSPQRYDEEPQUOTE 21
#define ONRTNEXCHANGESTATEINFO 22
#define ONRTNREQQUOTENOTICE 23
#define ONRSPACCOUNTRENTINFO 24
#define ONRSPTRADEMESSAGE 25
#define ONRTNTRADEMESSAGE 26
#define ONRSPQRYHISORDER 27
#define ONRSPQRYHISORDERPROCESS 28
#define ONRSPQRYHISFILL 29
#define ONRSPQRYHISPOSITION 30
#define ONRSPQRYHISDELIVERY 31
#define ONRSPQRYACCOUNTCASHADJUST 32
#define ONRSPQRYBILL 33
#define ONRSPACCOUNTFEERENT 34
#define ONRSPACCOUNTMARGINRENT 35
#define ONRSPADDMOBILEDEVICE 36
#define ONRSPQRYMANAGEINFOFORESTAR 37
#define ONRSPQRYSYSTEMPARAMETER 38
#define ONRSPQRYTRADECENTERFRONTADDRESS 39
#define ONRTNCOMMODITYINFO 40
#define ONRTNCURRENCYINFO 41
#define ONRSPQRYACCOUNTSTORAGE 42
#define ONRTNACCOUNTSTORAGE 43
#define ONRSPQRYSPOTLOCK 44
#define ONRTNSPOTLOCK 45
#define ONRSPSPECIALORDERACTION 46
#define ONRTNSPECIALORDER 47
#define ONRTNCOMBINEPOSITION 48
#define ONRTNCONTRACTQUOTE 49
#define ONRSPQRYTRUSTDEVICE 50
#define ONRSPADDTRUSTDEVICE 51
#define ONRSPDELTRUSTDEVICE 52
#define ONRTNADDUSERRIGHT 53
#define ONRTNDELUSERRIGHT 54
#define ONRSPQRYMANAGERCONFIGFILE 55


///-------------------------------------------------------------------------------------
///C++ SPI�Ļص���������ʵ��
///-------------------------------------------------------------------------------------

//API�ļ̳�ʵ��
class TdApi : public IEsTradeAPINotify
{
private:
	IEsTradeAPI* api;            //API����
    thread task_thread;                    //�����߳�ָ�루��python���������ݣ�
    TaskQueue task_queue;                //�������
    bool active = false;               //����״̬

public:
    TdApi()
    {
    };

    ~TdApi()
    {
        if (this->active)
        {
            this->exit();
        }
    };

    //-------------------------------------------------------------------------------------
    //API�ص�����
    //-------------------------------------------------------------------------------------

	virtual void ES_CDECL OnConnect(const TAPISTR_20 UserNo);
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
	virtual void ES_CDECL OnRspLogin(const TAPISTR_20 UserNo, TAPIINT32 nErrorCode, const TapAPITradeLoginRspInfo *pLoginRspInfo);
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
	virtual void ES_CDECL OnRtnContactInfo(const TAPISTR_20 UserNo, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPISecondInfo* pInfo);
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
	virtual void ES_CDECL OnRspRequestVertificateCode(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIVertificateCode *pInfo);
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
    virtual void ES_CDECL OnRspRequestVerifyIdentity(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIVerifyIdentity* pInfo);
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
    virtual void ES_CDECL OnRspSetVertificateCode(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPISecondCertificationRsp *pInfo);
    /**
	* @brief ��Ҫ������Ϣ��ʾ
	* @details ��API�ڲ��������ش���ʱ��ʾ�û�������Ϣ
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] ErrorMsg ������ʾ��Ϣ
	* @attention �ú����ص�����˵��API����ʱ�������ش���
    * 
	* @ingroup G_T_TradeSystem
	*/
	virtual void ES_CDECL OnRtnErrorMsg(const TAPISTR_20 UserNo, const TAPISTR_500 ErrorMsg);
	/**
	* @brief	֪ͨ�û�API׼������
	* @details	ֻ���û��ص��յ��˾���֪ͨʱ���ܽ��ж�Ӧ��¼�û������ĸ��ֲ������˻ص�������ĳ����¼�û��ܷ����������ı�־��
	* @param[in] UserNo ��¼�û�UserNo
	* @attention ������ſ��Խ��к�������
    * 
	* @ingroup G_T_Login
	*/
	virtual void ES_CDECL OnAPIReady(const TAPISTR_20 UserNo);
	/**
	* @brief API�ͷ���ʧȥ���ӵĻص�
	* @details ��APIʹ�ù������������߱��������������ʧȥ���Ӻ󶼻ᴥ���˻ص�֪ͨ�û���������������Ѿ��Ͽ���
	* @param[in] UserNo ��¼�û�UserNo
	* @param[in] nReasonCode �Ͽ�ԭ�����
    * 
	* @ingroup G_T_Disconnect
	*/
	virtual void ES_CDECL OnDisconnect(const TAPISTR_20 UserNo, TAPIINT32 nReasonCode);
	/**
	* @brief ֪ͨ�û��ύ�û���¼��Ϣ���(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nSessionID �ύ�û���¼��Ϣ������ID,��SubmitUserLoginInfo���ص�����ID��Ӧ
	* @param[in] pRspInfo ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
    * 
	* @ingroup G_T_UserInfo
	*/
	virtual void ES_CDECL OnRspSubmitUserLoginInfo(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, const TapAPISubmitUserLoginInfoRsp *pRspInfo);
	/**
	* @brief �û������޸�Ӧ��
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] nSessionID �޸����������ID,��ChangePassword������ID��Ӧ
	* @param[in] nErrorCode ���ش����룬0��ʾ�ɹ�
    * 
	* @ingroup G_T_UserInfo
	*/
	virtual void ES_CDECL OnRspChangePassword(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, TAPIINT32 nErrorCode, const TapAPIChangePasswordRsp* pInfo);
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
	virtual void ES_CDECL OnRspSetReservedInfo(const TAPISTR_20 UserNo, TAPIUINT32 nSessionID, TAPIINT32 nErrorCode, const TAPISTR_50 info);
	/**
	* @brief	����������Լ��Ϣ(�����ǡ�������ר��)
	* @details	���û������µĺ�Լ����Ҫ���������ڽ���ʱ����з�����������º�Լʱ�����û����������Լ����Ϣ��
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pRtnInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	* 
	* @ingroup G_T_Contract
	*/
	virtual void ES_CDECL OnRtnContract(const TAPISTR_20 UserNo, const TapAPITradeContractInfo *pRtnInfo);
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
	virtual void ES_CDECL OnRtnFund(const TAPISTR_20 UserNo, const TapAPIFundData *pRtnInfo);
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
	virtual void ES_CDECL OnRtnOrder(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPIOrderInfo *pRtnInfo);
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
    virtual void ES_CDECL OnRspOrderAction(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, const TapAPIOrderActionRsp *pRtnInfo);
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
	virtual void ES_CDECL OnRspQryOrderProcess(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIOrderInfo *pRspInfo);
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
	virtual void ES_CDECL OnRtnFill(const TAPISTR_20 UserNo, const TapAPIFillInfo *pRtnInfo);
	/**
	* @brief �ֱֲ仯����֪ͨ
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
	* @note �������ע�������ݣ������趨Loginʱ��NoticeIgnoreFlag�����Ρ�
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
	*/
	virtual void ES_CDECL OnRtnPosition(const TAPISTR_20 UserNo, const TapAPIPositionInfo *pRtnInfo);
	/**
	* @brief ƽ�����ݱ仯����(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
	* @note �������ע�������ݣ������趨Loginʱ��NoticeIgnoreFlag�����Ρ�
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
	*/
	virtual void ES_CDECL OnRtnClose(const TAPISTR_20 UserNo, const TapAPICloseInfo *pRtnInfo);
	/**
	* @brief �ֲ�ӯ��֪ͨ(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
	* @note �������ע�������ݣ������趨Loginʱ��NoticeIgnoreFlag�����Ρ�
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
	*/
	virtual void ES_CDECL OnRtnPositionProfit(const TAPISTR_20 UserNo, const TapAPIPositionProfitNotice *pRtnInfo);
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
	virtual void ES_CDECL OnRspQryDeepQuote(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIDeepQuoteQryRsp *pRspInfo);
	/**
	* @brief ������ʱ��״̬��Ϣ֪ͨ(������ר��)
	* @param[out] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[out] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeSystem
	*/
	virtual void ES_CDECL OnRtnExchangeStateInfo(const TAPISTR_20 UserNo, const TapAPIExchangeStateInfoNotice *pRtnInfo);
	/**
	* @brief ѯ��֪ͨ(�����ǡ�������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pRtnInfo ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
	*/
	virtual void ES_CDECL OnRtnReqQuoteNotice(const TAPISTR_20 UserNo, const TapAPIReqQuoteNotice *pRtnInfo);
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
	virtual void ES_CDECL OnRspAccountRentInfo(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIAccountRentInfo *pRspInfo);
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
	virtual void ES_CDECL OnRspTradeMessage(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPITradeMessage *pRspInfo);
    /**
	* @brief	������Ϣ֪ͨ
	* @details	�û��ڽ��׹����п�����Ϊ�ʽ𡢳ֲ֡�ƽ�ֵ�״̬�䶯ʹ�˻�����ĳЩΣ��״̬������ĳЩ��Ҫ����Ϣ��Ҫ���û�֪ͨ��
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pRtnInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention ��Ҫ�޸ĺ�ɾ��pRtnInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeSystem
	*/
	virtual void ES_CDECL OnRtnTradeMessage(const TAPISTR_20 UserNo, const TapAPITradeMessage *pRtnInfo);
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
	virtual void ES_CDECL OnRspQryHisOrder(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIHisOrderQryRsp *pInfo);
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
	virtual void ES_CDECL OnRspQryHisOrderProcess(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIHisOrderProcessQryRsp *pInfo);
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
	virtual void ES_CDECL OnRspQryHisFill(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIHisFillQryRsp *pInfo);
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
	virtual void ES_CDECL OnRspQryHisPosition(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIHisPositionQryRsp *pInfo);
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
	virtual void ES_CDECL OnRspQryHisDelivery(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIHisDeliveryQryRsp *pInfo);
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
	virtual void ES_CDECL OnRspQryAccountCashAdjust(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIAccountCashAdjustQryRsp *pInfo);
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
	virtual void ES_CDECL OnRspQryBill(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIBillQryRsp *pInfo);
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
	virtual void ES_CDECL OnRspAccountFeeRent(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIAccountFeeRentQryRsp *pInfo);
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
	virtual void ES_CDECL OnRspAccountMarginRent(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIAccountMarginRentQryRsp *pInfo);
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
	virtual void ES_CDECL OnRspAddMobileDevice(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIMobileDeviceAddRsp *pInfo);
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
	virtual void ES_CDECL OnRspQryManageInfoForEStar(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIManageInfo *pInfo);
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
	virtual void ES_CDECL OnRspQrySystemParameter(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPISystemParameterInfo *pInfo);
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
	virtual void ES_CDECL OnRspQryTradeCenterFrontAddress(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPITradeCenterFrontAddressInfo *pInfo);
	/**
	* @brief Ʒ����Ϣ֪ͨ(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_Commodity
	*/
	virtual void ES_CDECL OnRtnCommodityInfo(const TAPISTR_20 UserNo, const TapAPICommodityInfo *pInfo);
	/**
	* @brief ������Ϣ֪ͨ(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeSystem
	*/
	virtual void ES_CDECL OnRtnCurrencyInfo(const TAPISTR_20 UserNo, const TapAPICurrencyInfo *pInfo);
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
    virtual void ES_CDECL OnRspQryAccountStorage(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIAccountStorageInfo* pInfo);
    /**
    * @brief �ͻ��ֻ����֪ͨ(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
    */
    virtual void ES_CDECL OnRtnAccountStorage(const TAPISTR_20 UserNo, const TapAPIAccountStorageInfo* pInfo);
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
    virtual void ES_CDECL OnRspQrySpotLock(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPISpotLockInfo* pInfo);
    /**
    * @brief �ͻ��ֻ�������֪ͨ(������ר��)
	* @param[in] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[in] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions
    */
    virtual void ES_CDECL OnRtnSpotLock(const TAPISTR_20 UserNo, const TapAPISpotLockInfo* pInfo);
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
    virtual void ES_CDECL OnRspSpecialOrderAction(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, const TapAPISpecialOrderInfo *pRtnInfo);
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
    virtual void ES_CDECL OnRtnSpecialOrder(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, const TapAPISpecialOrderInfo* pInfo);
    /**
    * @brief �ͻ���ϳֲ�֪ͨ(ETFר��)
	* @param[out] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[out] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_ETF
    */
    virtual void ES_CDECL OnRtnCombinePosition(const TAPISTR_20 UserNo, const TapAPICombinePositionInfo* pInfo);
    /**
    * @brief ���׺�Լ������Ϣ֪ͨ(�����ǡ���Ʊר��)
	* @param[out] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[out] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_TradeActions 
    */
    virtual void ES_CDECL OnRtnContractQuote(const TAPISTR_20 UserNo, const TapAPIContractQuoteInfo* pInfo);
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
    virtual void ES_CDECL OnRspQryTrustDevice(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPITrustDeviceInfo* pInfo);
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
    virtual void ES_CDECL OnRspAddTrustDevice(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPITrustDeviceAddRsp* pInfo);
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
    virtual void ES_CDECL OnRspDelTrustDevice(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPITrustDeviceDelRsp* pInfo);
    /**
    * @brief �û�Ȩ������֪ͨ(������ר��)
	* @param[out] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[out] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_UserInfo 
    */
    virtual void ES_CDECL OnRtnAddUserRight(const TAPISTR_20 UserNo, const TapAPIUserRightInfo* pInfo);
    /**
    * @brief �û�Ȩ��ɾ��֪ͨ(������ר��)
	* @param[out] UserNo ָ�����Ϣ��Ӧ��UserNo
	* @param[out] pInfo	ָ�򷵻ص���Ϣ�ṹ��
	* @attention  ��Ҫ�޸ĺ�ɾ��pRspInfo��ָʾ�����ݣ��������ý���������������Ч��
	*
	* @ingroup G_T_UserInfo 
    */
    virtual void ES_CDECL OnRtnDelUserRight(const TAPISTR_20 UserNo, const TapAPIUserRightInfo* pInfo);
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
    virtual void ES_CDECL OnRspQryManagerConfigFile(const TAPISTR_20 UserNo, TAPIUINT32 nRequestID, TAPIINT32 nErrorCode, TAPIYNFLAG isLast, const TapAPIManagerConfigFileQryRsp* pInfo);



    //-------------------------------------------------------------------------------------
    //task������
    //-------------------------------------------------------------------------------------

	void processTask();

    void processConnect(Task *task);
    
    void processRspLogin(Task *task);
    
    void processRtnContactInfo(Task *task);
    
    void processRspRequestVertificateCode(Task *task);
    
    void processRspRequestVerifyIdentity(Task *task);
    
    void processRspSetVertificateCode(Task *task);
    
    void processRtnErrorMsg(Task *task);
    
    void processAPIReady(Task *task);
    
    void processDisconnect(Task *task);
    
    void processRspSubmitUserLoginInfo(Task *task);
    
    void processRspChangePassword(Task *task);
    
    void processRspSetReservedInfo(Task *task);
    
    void processRtnContract(Task *task);
    
    void processRtnFund(Task *task);
    
    void processRtnOrder(Task *task);
    
    void processRspOrderAction(Task *task);
    
    void processRspQryOrderProcess(Task *task);
    
    void processRtnFill(Task *task);
    
    void processRtnPosition(Task *task);
    
    void processRtnClose(Task *task);
    
    void processRtnPositionProfit(Task *task);
    
    void processRspQryDeepQuote(Task *task);
    
    void processRtnExchangeStateInfo(Task *task);
    
    void processRtnReqQuoteNotice(Task *task);
    
    void processRspAccountRentInfo(Task *task);
    
    void processRspTradeMessage(Task *task);
    
    void processRtnTradeMessage(Task *task);
    
    void processRspQryHisOrder(Task *task);
    
    void processRspQryHisOrderProcess(Task *task);
    
    void processRspQryHisFill(Task *task);
    
    void processRspQryHisPosition(Task *task);
    
    void processRspQryHisDelivery(Task *task);
    
    void processRspQryAccountCashAdjust(Task *task);
    
    void processRspQryBill(Task *task);
    
    void processRspAccountFeeRent(Task *task);
    
    void processRspAccountMarginRent(Task *task);
    
    void processRspAddMobileDevice(Task *task);
    
    void processRspQryManageInfoForEStar(Task *task);
    
    void processRspQrySystemParameter(Task *task);
    
    void processRspQryTradeCenterFrontAddress(Task *task);
    
    void processRtnCommodityInfo(Task *task);
    
    void processRtnCurrencyInfo(Task *task);
    
    void processRspQryAccountStorage(Task *task);
    
    void processRtnAccountStorage(Task *task);
    
    void processRspQrySpotLock(Task *task);
    
    void processRtnSpotLock(Task *task);
    
    void processRspSpecialOrderAction(Task *task);
    
    void processRtnSpecialOrder(Task *task);
    
    void processRtnCombinePosition(Task *task);
    
    void processRtnContractQuote(Task *task);
    
    void processRspQryTrustDevice(Task *task);
    
    void processRspAddTrustDevice(Task *task);
    
    void processRspDelTrustDevice(Task *task);
    
    void processRtnAddUserRight(Task *task);
    
    void processRtnDelUserRight(Task *task);
    
    void processRspQryManagerConfigFile(Task *task);



    //-------------------------------------------------------------------------------------
    //data���ص������������ֵ�
    //error���ص������Ĵ����ֵ�
    //id������id
    //last���Ƿ�Ϊ��󷵻�
    //i������
    //-------------------------------------------------------------------------------------
    
    virtual void onConnect(string UserNo) {};
    
    virtual void onRspLogin(string UserNo, int nErrorCode, const dict &data) {};
    
    virtual void onRtnContactInfo(string UserNo, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspRequestVertificateCode(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspRequestVerifyIdentity(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspSetVertificateCode(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRtnErrorMsg(string UserNo, string ErrorMsg) {};
    
    virtual void onAPIReady(string UserNo) {};
    
    virtual void onDisconnect(string UserNo, int nReasonCode) {};
    
    virtual void onRspSubmitUserLoginInfo(string UserNo, unsigned int session, const dict &data) {};
    
    virtual void onRspChangePassword(string UserNo, unsigned int session, int nErrorCode, const dict &data) {};
    
    virtual void onRspSetReservedInfo(string UserNo, unsigned int session, int nErrorCode, string info) {};
    
    virtual void onRtnContract(string UserNo, const dict &data) {};
    
    virtual void onRtnFund(string UserNo, const dict &data) {};
    
    virtual void onRtnOrder(string UserNo, unsigned int session, const dict &data) {};
    
    virtual void onRspOrderAction(string UserNo, unsigned int session, int nErrorCode, const dict &data) {};
    
    virtual void onRspQryOrderProcess(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRtnFill(string UserNo, const dict &data) {};
    
    virtual void onRtnPosition(string UserNo, const dict &data) {};
    
    virtual void onRtnClose(string UserNo, const dict &data) {};
    
    virtual void onRtnPositionProfit(string UserNo, const dict &data) {};
    
    virtual void onRspQryDeepQuote(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRtnExchangeStateInfo(string UserNo, const dict &data) {};
    
    virtual void onRtnReqQuoteNotice(string UserNo, const dict &data) {};
    
    virtual void onRspAccountRentInfo(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspTradeMessage(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRtnTradeMessage(string UserNo, const dict &data) {};
    
    virtual void onRspQryHisOrder(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspQryHisOrderProcess(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspQryHisFill(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspQryHisPosition(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspQryHisDelivery(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspQryAccountCashAdjust(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspQryBill(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspAccountFeeRent(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspAccountMarginRent(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspAddMobileDevice(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspQryManageInfoForEStar(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspQrySystemParameter(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspQryTradeCenterFrontAddress(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRtnCommodityInfo(string UserNo, const dict &data) {};
    
    virtual void onRtnCurrencyInfo(string UserNo, const dict &data) {};
    
    virtual void onRspQryAccountStorage(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRtnAccountStorage(string UserNo, const dict &data) {};
    
    virtual void onRspQrySpotLock(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRtnSpotLock(string UserNo, const dict &data) {};
    
    virtual void onRspSpecialOrderAction(string UserNo, unsigned int session, int nErrorCode, const dict &data) {};
    
    virtual void onRtnSpecialOrder(string UserNo, unsigned int session, const dict &data) {};
    
    virtual void onRtnCombinePosition(string UserNo, const dict &data) {};
    
    virtual void onRtnContractQuote(string UserNo, const dict &data) {};
    
    virtual void onRspQryTrustDevice(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspAddTrustDevice(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRspDelTrustDevice(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};
    
    virtual void onRtnAddUserRight(string UserNo, const dict &data) {};
    
    virtual void onRtnDelUserRight(string UserNo, const dict &data) {};
    
    virtual void onRspQryManagerConfigFile(string UserNo, unsigned int session, int nErrorCode, char last, const dict &data) {};



    //-------------------------------------------------------------------------------------
    //req:���������������ֵ�
    //-------------------------------------------------------------------------------------
	void createEsTradeAPI(int nResult);

	void release();

	void init();

	int exit();

	int esunny_getloginInfo(const dict&req);

	string getEsTradeAPIVersion();

	int setEsTradeAPIDataPath(string pPath);

	int setEsTradeAPILogLevel(string LogLevel);

	int setUserInfo(const dict &req);

	int setBackUpAddress(string UserNo, const dict &req);

	pybind11::tuple requestVerifyIdentity(string UserNo, const dict &req, TAPIUINT32 nRequestID);

	int startUser(string UserNo, const dict &req);

	int stopUser(string UserNo);

	pybind11::tuple requestVertificateCode(string UserNo, const dict &req, TAPIUINT32 nRequestID);

	pybind11::tuple setVertificateCode(string UserNo, const dict &req, TAPIUINT32 nRequestID);

	pybind11::tuple insertOrder(string UserNo, const dict &req, TAPIUINT32 nRequestID);

	pybind11::tuple cancelOrder(string UserNo, const dict &req, TAPIUINT32 nRequestID);

    pybind11::tuple qryOrderProcess(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryDeepQuote(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryAccountRent(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryAccountFeeRent(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryAccountMarginRent(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryAccountCashAdjust(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryBill(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryHisOrder(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryHisOrderProcess(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryHisFill(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryHisPosition(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryHisDelivery(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryManageInfoForEStar(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qrySystemParameter(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryTradeCenterFrontAddress(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryTradeMessage(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryAccountStorage(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qrySpotLock(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryTrustDevice(string UserNo, const dict &data, TAPIUINT32 nRequestID);
    
    pybind11::tuple qryManagerConfigFile(string UserNo, const dict &data, TAPIUINT32 nRequestID);

};
