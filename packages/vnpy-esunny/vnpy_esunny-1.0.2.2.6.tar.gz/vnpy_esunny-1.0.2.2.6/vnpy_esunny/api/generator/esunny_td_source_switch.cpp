case ONCONNECT:
{
	this->processConnect(&task);
	break;
}

case ONRSPLOGIN:
{
	this->processRspLogin(&task);
	break;
}

case ONRTNCONTACTINFO:
{
	this->processRtnContactInfo(&task);
	break;
}

case ONRSPREQUESTVERTIFICATECODE:
{
	this->processRspRequestVertificateCode(&task);
	break;
}

case ONRSPREQUESTVERIFYIDENTITY:
{
	this->processRspRequestVerifyIdentity(&task);
	break;
}

case ONRSPSETVERTIFICATECODE:
{
	this->processRspSetVertificateCode(&task);
	break;
}

case ONRTNERRORMSG:
{
	this->processRtnErrorMsg(&task);
	break;
}

case ONAPIREADY:
{
	this->processAPIReady(&task);
	break;
}

case ONDISCONNECT:
{
	this->processDisconnect(&task);
	break;
}

case ONRSPSUBMITUSERLOGININFO:
{
	this->processRspSubmitUserLoginInfo(&task);
	break;
}

case ONRSPCHANGEPASSWORD:
{
	this->processRspChangePassword(&task);
	break;
}

case ONRSPSETRESERVEDINFO:
{
	this->processRspSetReservedInfo(&task);
	break;
}

case ONRTNCONTRACT:
{
	this->processRtnContract(&task);
	break;
}

case ONRTNFUND:
{
	this->processRtnFund(&task);
	break;
}

case ONRTNORDER:
{
	this->processRtnOrder(&task);
	break;
}

case ONRSPORDERACTION:
{
	this->processRspOrderAction(&task);
	break;
}

case ONRSPQRYORDERPROCESS:
{
	this->processRspQryOrderProcess(&task);
	break;
}

case ONRTNFILL:
{
	this->processRtnFill(&task);
	break;
}

case ONRTNPOSITION:
{
	this->processRtnPosition(&task);
	break;
}

case ONRTNCLOSE:
{
	this->processRtnClose(&task);
	break;
}

case ONRTNPOSITIONPROFIT:
{
	this->processRtnPositionProfit(&task);
	break;
}

case ONRSPQRYDEEPQUOTE:
{
	this->processRspQryDeepQuote(&task);
	break;
}

case ONRTNEXCHANGESTATEINFO:
{
	this->processRtnExchangeStateInfo(&task);
	break;
}

case ONRTNREQQUOTENOTICE:
{
	this->processRtnReqQuoteNotice(&task);
	break;
}

case ONRSPACCOUNTRENTINFO:
{
	this->processRspAccountRentInfo(&task);
	break;
}

case ONRSPTRADEMESSAGE:
{
	this->processRspTradeMessage(&task);
	break;
}

case ONRTNTRADEMESSAGE:
{
	this->processRtnTradeMessage(&task);
	break;
}

case ONRSPQRYHISORDER:
{
	this->processRspQryHisOrder(&task);
	break;
}

case ONRSPQRYHISORDERPROCESS:
{
	this->processRspQryHisOrderProcess(&task);
	break;
}

case ONRSPQRYHISFILL:
{
	this->processRspQryHisFill(&task);
	break;
}

case ONRSPQRYHISPOSITION:
{
	this->processRspQryHisPosition(&task);
	break;
}

case ONRSPQRYHISDELIVERY:
{
	this->processRspQryHisDelivery(&task);
	break;
}

case ONRSPQRYACCOUNTCASHADJUST:
{
	this->processRspQryAccountCashAdjust(&task);
	break;
}

case ONRSPQRYBILL:
{
	this->processRspQryBill(&task);
	break;
}

case ONRSPACCOUNTFEERENT:
{
	this->processRspAccountFeeRent(&task);
	break;
}

case ONRSPACCOUNTMARGINRENT:
{
	this->processRspAccountMarginRent(&task);
	break;
}

case ONRSPADDMOBILEDEVICE:
{
	this->processRspAddMobileDevice(&task);
	break;
}

case ONRSPQRYMANAGEINFOFORESTAR:
{
	this->processRspQryManageInfoForEStar(&task);
	break;
}

case ONRSPQRYSYSTEMPARAMETER:
{
	this->processRspQrySystemParameter(&task);
	break;
}

case ONRSPQRYTRADECENTERFRONTADDRESS:
{
	this->processRspQryTradeCenterFrontAddress(&task);
	break;
}

case ONRTNCOMMODITYINFO:
{
	this->processRtnCommodityInfo(&task);
	break;
}

case ONRTNCURRENCYINFO:
{
	this->processRtnCurrencyInfo(&task);
	break;
}

case ONRSPQRYACCOUNTSTORAGE:
{
	this->processRspQryAccountStorage(&task);
	break;
}

case ONRTNACCOUNTSTORAGE:
{
	this->processRtnAccountStorage(&task);
	break;
}

case ONRSPQRYSPOTLOCK:
{
	this->processRspQrySpotLock(&task);
	break;
}

case ONRTNSPOTLOCK:
{
	this->processRtnSpotLock(&task);
	break;
}

case ONRSPSPECIALORDERACTION:
{
	this->processRspSpecialOrderAction(&task);
	break;
}

case ONRTNSPECIALORDER:
{
	this->processRtnSpecialOrder(&task);
	break;
}

case ONRTNCOMBINEPOSITION:
{
	this->processRtnCombinePosition(&task);
	break;
}

case ONRTNCONTRACTQUOTE:
{
	this->processRtnContractQuote(&task);
	break;
}

case ONRSPQRYTRUSTDEVICE:
{
	this->processRspQryTrustDevice(&task);
	break;
}

case ONRSPADDTRUSTDEVICE:
{
	this->processRspAddTrustDevice(&task);
	break;
}

case ONRSPDELTRUSTDEVICE:
{
	this->processRspDelTrustDevice(&task);
	break;
}

case ONRTNADDUSERRIGHT:
{
	this->processRtnAddUserRight(&task);
	break;
}

case ONRTNDELUSERRIGHT:
{
	this->processRtnDelUserRight(&task);
	break;
}

case ONRSPQRYMANAGERCONFIGFILE:
{
	this->processRspQryManagerConfigFile(&task);
	break;
}

