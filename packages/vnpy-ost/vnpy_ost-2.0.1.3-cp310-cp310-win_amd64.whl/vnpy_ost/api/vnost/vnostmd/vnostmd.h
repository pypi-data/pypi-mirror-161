//ϵͳ
#ifdef WIN32
#include "stdafx.h"
#endif

#include "vnost.h"
#include "pybind11/pybind11.h"
#include "ost/SecurityDntL2MDUserApi.h"


using namespace pybind11;

//����
#define ONRSPSUBL2MARKETDATA 0
#define ONRSPUNSUBL2MARKETDATA 1
#define ONRSPSUBL2ORDERANDTRADE 2
#define ONRSPUNSUBL2ORDERANDTRADE 3
#define ONRSPSUBL2INDEXMARKETDATA 4
#define ONRSPUNSUBL2INDEXMARKETDATA 5
#define ONRTNL2MARKETDATA 6
#define ONRTNL2INDEXMARKETDATA 7
#define ONRTNL2ORDER 8
#define ONRTNL2TRADE 9


///-------------------------------------------------------------------------------------
///C++ SPI�Ļص���������ʵ��
///-------------------------------------------------------------------------------------

//API�ļ̳�ʵ��
using namespace _DNT_;
class MdApi : public CSecurityDntL2MDUserSpi
{
private:
	CSecurityDntL2MDUserApi* api;				//API����
	thread task_thread;					//�����߳�ָ�루��python���������ݣ�
	TaskQueue task_queue;			    //�������
	bool active = false;				//����״̬

public:
	MdApi()
	{
	};

	~MdApi()
	{
		if (this->active)
		{
			this->exit();
		}
	};

	//-------------------------------------------------------------------------------------
	//API�ص�����
	//-------------------------------------------------------------------------------------

	/// ����L2����Ӧ��
	virtual void OnRspSubL2MarketData(const CSecurityDntRspInfoField& reply);

	/// ȡ������Level2����Ӧ��
	virtual void OnRspUnSubL2MarketData(const CSecurityDntRspInfoField& reply);

	/// ��ʶ���Ӧ��
	virtual void OnRspSubL2OrderAndTrade(const CSecurityDntRspInfoField& reply);

	/// ȡ����ʶ���Ӧ��
	virtual void OnRspUnSubL2OrderAndTrade(const CSecurityDntRspInfoField& reply);

	/// ָ������Ӧ��
	virtual void OnRspSubL2IndexMarketData(const CSecurityDntRspInfoField& reply);

	/// ȡ��ָ������Ӧ��
	virtual void OnRspUnSubL2IndexMarketData(const CSecurityDntRspInfoField& reply);

	/// Level2����֪ͨ
	virtual void OnRtnL2MarketData(const CSecurityDntMarketDataField& reply);

	/// Level2ָ��֪ͨ
	virtual void OnRtnL2IndexMarketData(const CSecurityDntL2IndexField& reply);

	/// Level2���ί������֪ͨ
	virtual void OnRtnL2Order(const CSecurityDntL2OrderField& pL2Order);

	/// Level2��ʳɽ�����֪ͨ
	virtual void OnRtnL2Trade(const CSecurityDntL2TradeField& pL2Trade);

    //-------------------------------------------------------------------------------------
    //task������
    //-------------------------------------------------------------------------------------

	void processTask();

    void processRspSubL2MarketData(Task *task);
    
    void processRspUnSubL2MarketData(Task *task);
    
    void processRspSubL2OrderAndTrade(Task *task);
    
    void processRspUnSubL2OrderAndTrade(Task *task);
    
    void processRspSubL2IndexMarketData(Task *task);
    
    void processRspUnSubL2IndexMarketData(Task *task);
    
    void processRtnL2MarketData(Task *task);
    
    void processRtnL2IndexMarketData(Task *task);
    
    void processRtnL2Order(Task *task);
    
    void processRtnL2Trade(Task *task);

	//-------------------------------------------------------------------------------------
    //data���ص������������ֵ�
    //error���ص������Ĵ����ֵ�
    //id������id
    //last���Ƿ�Ϊ��󷵻�
    //i������
    //-------------------------------------------------------------------------------------

    virtual void onRspSubL2MarketData(const dict &data) {};
    
    virtual void onRspUnSubL2MarketData(const dict &data) {};
    
    virtual void onRspSubL2OrderAndTrade(const dict &data) {};
    
    virtual void onRspUnSubL2OrderAndTrade(const dict &data) {};
    
    virtual void onRspSubL2IndexMarketData(const dict &data) {};
    
    virtual void onRspUnSubL2IndexMarketData(const dict &data) {};
    
    virtual void onRtnL2MarketData(const dict &data) {};
    
    virtual void onRtnL2IndexMarketData(const dict &data) {};
    
    virtual void onRtnL2Order(const dict &data) {};
    
    virtual void onRtnL2Trade(const dict &data) {};

	//-------------------------------------------------------------------------------------
    //req:���������������ֵ�
    //-------------------------------------------------------------------------------------

	void createCSecurityDntL2MDUserApi();

	void release();

	int exit();

	void registerFront(const dict &sh_req, const dict &sz_req, uint32_t len);

	int subscribeL2MarketData(const dict &req);

	int unSubscribeL2MarketData(const dict &req);

	int subscribeL2OrderAndTrade();

	int unSubscribeL2OrderAndTrade();

	int subscribeL2IndexMarketData();

	int unSubscribeL2IndexMarketData();

};