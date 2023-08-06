//ϵͳ
#ifdef WIN32
#include "stdafx.h"
#endif

#include "vnost.h"
#include "pybind11/pybind11.h"
#include "ost/UTApi.h"


using namespace pybind11;

//����
#define ONFRONTCONNECTED 0
#define ONFRONTDISCONNECTED 1
#define ONRSPERROR 2
#define ONRTNORDER 3
#define ONRTNTRADE 4
#define ONERRRTNORDERACTION 5
#define ONRSPORDERINSERT 6
#define ONRSPORDERACTION 7
#define ONRSPLOGIN 8
#define ONRSPUSERPASSWORDUPDATE 9
#define ONRSPTRANSFERINSERT 10
#define ONRTNTRANSFER 11
#define ONRSPFUNDPAYBACKINSERT 12
#define ONRTNFUNDPAYBACK 13
#define ONRSPSTOCKPAYBACKINSERT 14
#define ONRTNSTOCKPAYBACK 15
#define ONRTNPRIVATECREDITSTOCK 16
#define ONRTNLOCK 17
#define ONRSPLOCKINSERT 18
#define ONRTNEXECORDER 19
#define ONRSPEXECORDERINSERT 20
#define ONRSPEXECORDERACTION 21
#define ONERRRTNEXECORDERACTION 22
#define ONRSPQRYINSTRUMENT 23
#define ONRSPQRYDEPTHMARKETDATA 24
#define ONRSPQRYINVESTORPOSITION 25
#define ONRSPQRYTRADINGACCOUNT 26
#define ONRSPQRYOPTIONINSTRMARGINBYVOLUME 27
#define ONRSPQRYOPTIONINSTRCOMMRATE 28
#define ONRSPQRYORDER 29
#define ONRSPQRYTRADE 30
#define ONRSPQRYINSTRUMENTCOMMISSIONRATE 31
#define ONRSPQRYINVESTOR 32
#define ONRSPQRYTRANSFER 33
#define ONRSPQRYTRADINGCODE 34
#define ONRSPQRYMAXORDERVOLUME 35
#define ONRSPQRYCREDITINSTRUMENT 36
#define ONRSPQRYCREDITINVESTOR 37
#define ONRSPQRYPRIVATECREDITSTOCK 38
#define ONRSPQRYCREDITCONCENTRATION 39
#define ONRSPQRYCREDITFUNDDETAIL 40
#define ONRSPQRYCREDITSTOCKDETAIL 41
#define ONRSPQRYFUNDPAYBACK 42
#define ONRSPQRYSTOCKPAYBACK 43
#define ONRSPQRYPUBLICCREDITFUND 44
#define ONRSPQRYETFINFO 45
#define ONRSPQRYETFCOMPONENT 46
#define ONRSPQRYCREDITAVAILABLEDETAIL 47
#define ONRSPQRYLOCK 48
#define ONRSPQRYEXECORDER 49
#define ONRSPQRYLOCKPOSITION 50
#define ONRSPQRYOPTPOSILIMIT 51
#define ONRSPQRYOPTAMOUNTLIMIT 52

///-------------------------------------------------------------------------------------
///C++ SPI�Ļص���������ʵ��
///-------------------------------------------------------------------------------------

//API�ļ̳�ʵ��
class TdApi : public CUTSpi
{
private:
	CUTApi* api;            //API����
	thread task_thread;                    //�����߳�ָ�루��python���������ݣ�
	TaskQueue task_queue;                //�������
	bool active = false;                //����״̬

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

	///���ͻ����뽻�׺�̨������ͨ������ʱ����δ��¼ǰ�����÷��������á�
	virtual void OnFrontConnected();

	///���ͻ����뽻�׺�̨ͨ�����ӶϿ�ʱ���÷��������á���������������API���Զ��������ӣ��ͻ��˿ɲ�������
	///@param nReason ����ԭ��
	///        0x1001 �����ʧ��
	///        0x1002 ����дʧ��
	///        0x2001 ����������ʱ
	///        0x2002 ��������ʧ��
	///        0x2003 �յ�������
	virtual void OnFrontDisconnected(int nReason);

	//�����̨��֧�ֵĹ���ʱ����
	virtual void OnRspError(CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///����
	virtual void OnRtnOrder(CUTOrderField *pOrder);

	///�ɽ�
	virtual void OnRtnTrade(CUTTradeField *pTrade);

	///���������ر�
	virtual void OnErrRtnOrderAction(CUTOrderActionField *pOrderAction);


	///��������ر�
	virtual void OnRspOrderInsert(CUTInputOrderField *pInputOrder, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///���������ر�
	virtual void OnRspOrderAction(CUTInputOrderActionField *pInputOrderAction, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�û�����Ӧ��
	virtual void OnRspLogin(CUTRspLoginField *pRspLogin, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����޸�Ӧ��
	virtual void OnRspUserPasswordUpdate(CUTUserPasswordUpdateField *pUserPasswordUpdate, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///ת�˴���ر�
	virtual void OnRspTransferInsert(CUTInputTransferField *pInputTransfer, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///ת��
	virtual void OnRtnTransfer(CUTTransferField *pTransfer);

	///ֱ�ӻ������ر�
	virtual void OnRspFundPaybackInsert(CUTInputFundPaybackField *pInputFundPayback, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///ֱ�ӻ���
	virtual void OnRtnFundPayback(CUTFundPaybackField *pFundPayback);

	///ֱ�ӻ�ȯ����ر�
	virtual void OnRspStockPaybackInsert(CUTInputStockPaybackField *pInputStockPayback, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///ֱ�ӻ�ȯ
	virtual void OnRtnStockPayback(CUTStockPaybackField *pStockPayback);

	///ͬ��������ص�ȯԴ���׶����Ϣ
	virtual void OnRtnPrivateCreditStock(CUTPrivateCreditStockField *pPrivateCreditStock);

	///����
	virtual void OnRtnLock(CUTLockField *pLock);

	///��������ر�
	virtual void OnRspLockInsert(CUTInputLockField *pInputLock, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///��Ȩ
	virtual void OnRtnExecOrder(CUTExecOrderField *pExecOrder);

	///��Ȩ����ر�
	virtual void OnRspExecOrderInsert(CUTInputExecOrderField *pInputExecOrder, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///��Ȩ�����ر�
	virtual void OnRspExecOrderAction(CUTInputExecOrderActionField *pInputExecOrderAction, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///��Ȩ�����ر�
	virtual void OnErrRtnExecOrderAction(CUTExecOrderActionField *pExecOrderAction);


	///�����ѯ��Լ��Ӧ
	virtual void OnRspQryInstrument(CUTInstrumentField *pInstrument, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ������Ӧ
	virtual void OnRspQryDepthMarketData(CUTDepthMarketDataField *pDepthMarketData, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ�ֲ���Ӧ
	virtual void OnRspQryInvestorPosition(CUTInvestorPositionField *pInvestorPosition, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ�ʽ���Ӧ
	virtual void OnRspQryTradingAccount(CUTTradingAccountField *pTradingAccount, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ��Ȩ��Լÿ�ֱ�֤����Ӧ
	virtual void OnRspQryOptionInstrMarginByVolume(CUTOptionInstrMarginByVolumeField *pOptionInstrMarginByVolume, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ��Ȩ����������Ӧ
	virtual void OnRspQryOptionInstrCommRate(CUTOptionInstrCommRateField *pOptionInstrCommRate, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ������Ӧ
	virtual void OnRspQryOrder(CUTOrderField *pOrder, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ�ɽ���Ӧ
	virtual void OnRspQryTrade(CUTTradeField *pTrade, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ����������Ӧ
	virtual void OnRspQryInstrumentCommissionRate(CUTInstrumentCommissionRateField *pInstrumentCommissionRate, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯͶ������Ӧ
	virtual void OnRspQryInvestor(CUTInvestorField *pInvestor, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯת����Ӧ
	virtual void OnRspQryTransfer(CUTTransferField *pTransfer, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ���ױ���
	virtual void OnRspQryTradingCode(CUTTradingCodeField *pTradingCode, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///��ѯ����µ�����Ӧ
	virtual void OnRspQryMaxOrderVolume(CUTMaxOrderVolumeField *pMaxOrderVolume, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ���ú�Լ������Ӧ
	virtual void OnRspQryCreditInstrument(CUTCreditInstrumentField *pCreditInstrument, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯͶ����������Ϣ��Ӧ
	virtual void OnRspQryCreditInvestor(CUTCreditInvestorField *pCreditInvestor, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯͶ���߿���ȯ��Ӧ
	virtual void OnRspQryPrivateCreditStock(CUTPrivateCreditStockField *pPrivateCreditStock, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ���жȲ�����Ӧ
	virtual void OnRspQryCreditConcentration(CUTCreditConcentrationField *pCreditConcentration, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯͶ����������ϸ��Ӧ
	virtual void OnRspQryCreditFundDetail(CUTCreditFundDetailField *pCreditFundDetail, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯͶ������ȯ��ϸ��Ӧ
	virtual void OnRspQryCreditStockDetail(CUTCreditStockDetailField *pCreditStockDetail, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯͶ����ֱ�ӻ�����Ӧ
	virtual void OnRspQryFundPayback(CUTFundPaybackField *pFundPayback, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯͶ����ֱ�ӻ�ȯ��Ӧ
	virtual void OnRspQryStockPayback(CUTStockPaybackField *pStockPayback, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ�������ʶ����Ӧ
	virtual void OnRspQryPublicCreditFund(CUTPublicCreditFundField *pPublicCreditFund, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯETF��Ϣ��Ӧ
	virtual void OnRspQryETFInfo(CUTETFInfoField *pETFInfo, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯETF�ɷֹ���Ӧ
	virtual void OnRspQryETFComponent(CUTETFComponentField *pETFComponent, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ��֤����������ϸ��Ӧ
	virtual void OnRspQryCreditAvailableDetail(CUTCreditAvailableDetailField *pCreditAvailableDetail, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ������Ӧ
	virtual void OnRspQryLock(CUTLockField *pLock, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ��Ȩ��Ӧ
	virtual void OnRspQryExecOrder(CUTExecOrderField *pExecOrder, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ������λ��Ӧ
	virtual void OnRspQryLockPosition(CUTLockPositionField *pLockPosition, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ��Ȩ�޲���Ӧ
	virtual void OnRspQryOptPosiLimit(CUTOptPosiLimitField *pOptPosiLimit, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ��Ȩ�޶���Ӧ
	virtual void OnRspQryOptAmountLimit(CUTOptAmountLimitField *pOptAmountLimit, CUTRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

	//-------------------------------------------------------------------------------------
	//task������
	//-------------------------------------------------------------------------------------
	void processTask();

	void processFrontConnected(Task *task);

	void processFrontDisconnected(Task *task);

	void processRspError(Task *task);

	void processRtnOrder(Task *task);

	void processRtnTrade(Task *task);

	void processErrRtnOrderAction(Task *task);

	void processRspOrderInsert(Task *task);

	void processRspOrderAction(Task *task);

	void processRspLogin(Task *task);

	void processRspUserPasswordUpdate(Task *task);

	void processRspTransferInsert(Task *task);

	void processRtnTransfer(Task *task);

	void processRspFundPaybackInsert(Task *task);

	void processRtnFundPayback(Task *task);

	void processRspStockPaybackInsert(Task *task);

	void processRtnStockPayback(Task *task);

	void processRtnPrivateCreditStock(Task *task);

	void processRtnLock(Task *task);

	void processRspLockInsert(Task *task);

	void processRtnExecOrder(Task *task);

	void processRspExecOrderInsert(Task *task);

	void processRspExecOrderAction(Task *task);

	void processErrRtnExecOrderAction(Task *task);

	void processRspQryInstrument(Task *task);

	void processRspQryDepthMarketData(Task *task);

	void processRspQryInvestorPosition(Task *task);

	void processRspQryTradingAccount(Task *task);

	void processRspQryOptionInstrMarginByVolume(Task *task);

	void processRspQryOptionInstrCommRate(Task *task);

	void processRspQryOrder(Task *task);

	void processRspQryTrade(Task *task);

	void processRspQryInstrumentCommissionRate(Task *task);

	void processRspQryInvestor(Task *task);

	void processRspQryTransfer(Task *task);

	void processRspQryTradingCode(Task *task);

	void processRspQryMaxOrderVolume(Task *task);

	void processRspQryCreditInstrument(Task *task);

	void processRspQryCreditInvestor(Task *task);

	void processRspQryPrivateCreditStock(Task *task);

	void processRspQryCreditConcentration(Task *task);

	void processRspQryCreditFundDetail(Task *task);

	void processRspQryCreditStockDetail(Task *task);

	void processRspQryFundPayback(Task *task);

	void processRspQryStockPayback(Task *task);

	void processRspQryPublicCreditFund(Task *task);

	void processRspQryETFInfo(Task *task);

	void processRspQryETFComponent(Task *task);

	void processRspQryCreditAvailableDetail(Task *task);

	void processRspQryLock(Task *task);

	void processRspQryExecOrder(Task *task);

	void processRspQryLockPosition(Task *task);

	void processRspQryOptPosiLimit(Task *task);

	void processRspQryOptAmountLimit(Task *task);

	//-------------------------------------------------------------------------------------
	//data���ص������������ֵ�
	//error���ص������Ĵ����ֵ�
	//id������id
	//last���Ƿ�Ϊ��󷵻�
	//i������
	//-------------------------------------------------------------------------------------

	virtual void onFrontConnected() {};

	virtual void onFrontDisconnected(int reqid) {};

	virtual void onRspError(const dict &error, int reqid, bool last) {};

	virtual void onRtnOrder(const dict &data) {};

	virtual void onRtnTrade(const dict &data) {};

	virtual void onErrRtnOrderAction(const dict &data) {};

	virtual void onRspOrderInsert(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspOrderAction(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspLogin(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspUserPasswordUpdate(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspTransferInsert(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRtnTransfer(const dict &data) {};

	virtual void onRspFundPaybackInsert(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRtnFundPayback(const dict &data) {};

	virtual void onRspStockPaybackInsert(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRtnStockPayback(const dict &data) {};

	virtual void onRtnPrivateCreditStock(const dict &data) {};

	virtual void onRtnLock(const dict &data) {};

	virtual void onRspLockInsert(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRtnExecOrder(const dict &data) {};

	virtual void onRspExecOrderInsert(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspExecOrderAction(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onErrRtnExecOrderAction(const dict &data) {};

	virtual void onRspQryInstrument(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryDepthMarketData(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryInvestorPosition(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryTradingAccount(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryOptionInstrMarginByVolume(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryOptionInstrCommRate(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryOrder(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryTrade(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryInstrumentCommissionRate(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryInvestor(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryTransfer(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryTradingCode(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryMaxOrderVolume(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryCreditInstrument(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryCreditInvestor(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryPrivateCreditStock(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryCreditConcentration(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryCreditFundDetail(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryCreditStockDetail(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryFundPayback(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryStockPayback(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryPublicCreditFund(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryETFInfo(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryETFComponent(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryCreditAvailableDetail(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryLock(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryExecOrder(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryLockPosition(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryOptPosiLimit(const dict &data, const dict &error, int reqid, bool last) {};

	virtual void onRspQryOptAmountLimit(const dict &data, const dict &error, int reqid, bool last) {};

	//-------------------------------------------------------------------------------------
	//req:���������������ֵ�
	//-------------------------------------------------------------------------------------

	void createApi(string pszFlowPath = "", int nCPUID = 0);

	void release();

	void init();

	int join();

	int exit();

	string getApiVersion();

	void registerFront(string pszFrontAddress);

	void subscribePrivateTopic(int nResumeType);

	void subscribePublicTopic(int nResumeType);

	void submitTerminalInfo(const dict &req);

	int reqOrderInsert(const dict &req, int reqid);

	int reqOrderAction(const dict &req, int reqid);

	int reqLogin(const dict &req, int reqid);

	int reqLogout(const dict &req, int reqid);

	int reqUserPasswordUpdate(const dict &req, int reqid);

	int reqTransferInsert(const dict &req, int reqid);

	int reqFundPaybackInsert(const dict &req, int reqid);

	int reqStockPaybackInsert(const dict &req, int reqid);

	int reqLockInsert(const dict &req, int reqid);

	int reqExecOrderInsert(const dict &req, int reqid);

	int reqExecOrderAction(const dict &req, int reqid);

	int reqQryInstrument(const dict &req, int reqid);

	int reqQryDepthMarketData(const dict &req, int reqid);

	int reqQryInvestorPosition(const dict &req, int reqid);

	int reqQryTradingAccount(const dict &req, int reqid);

	int reqQryOrder(const dict &req, int reqid);

	int reqQryTrade(const dict &req, int reqid);

	int reqQryOptionInstrMarginByVolume(const dict &req, int reqid);

	int reqQryOptionInstrCommRate(const dict &req, int reqid);

	int reqQryInstrumentCommissionRate(const dict &req, int reqid);

	int reqQryInvestor(const dict &req, int reqid);

	int reqQryTransfer(const dict &req, int reqid);

	int reqQryTradingCode(const dict &req, int reqid);

	int reqQryMaxOrderVolume(const dict &req, int reqid);

	int reqQryCreditInstrument(const dict &req, int reqid);

	int reqQryCreditInvestor(const dict &req, int reqid);

	int reqQryPrivateCreditStock(const dict &req, int reqid);

	int reqQryCreditConcentration(const dict &req, int reqid);

	int reqQryCreditFundDetail(const dict &req, int reqid);

	int reqQryCreditStockDetail(const dict &req, int reqid);

	int reqQryFundPayback(const dict &req, int reqid);

	int reqQryStockPayback(const dict &req, int reqid);

	int reqQryPublicCreditFund(const dict &req, int reqid);

	int reqQryETFInfo(const dict &req, int reqid);

	int reqQryETFComponent(const dict &req, int reqid);

	int reqQryCreditAvailableDetail(const dict &req, int reqid);

	int reqQryLock(const dict &req, int reqid);

	int reqQryExecOrder(const dict &req, int reqid);

	int reqQryLockPosition(const dict &req, int reqid);

	int reqQryOptPosiLimit(const dict &req, int reqid);

	int reqQryOptAmountLimit(const dict &req, int reqid);
};