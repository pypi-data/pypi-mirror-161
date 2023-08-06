#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
from lazysdk import lazyrequests
from lazysdk import lazymd5
import time


def get_sign(
        distributor_id,  # 分销商标识
        secret_key,  # 签名密钥
        ts=None  # 时间戳
):
    """
    生成签名
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥
    :param ts: 时间戳
    """
    if ts is None:
        ts = int(time.time())
    param_str = str(distributor_id) + str(secret_key) + str(ts)
    return lazymd5.md5_str(content=param_str)


def get_charge(
        distributor_id,
        secret_key,
        begin=None,
        end=None,
        offset=None,
        limit=None,
        device_id=None,
        outside_trade_no=None,
        paid=None,
        optimizer_account=None,
        open_id=None
):
    """
    获取用户充值事件
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥
    :param begin: 数据查询开始时间点（unix 时间戳），默认为上一个小时开始时间点，最大支持获取3天内数据-订单创建时间
    :param end: 数据查询截止时间点（unix 时间戳），默认为当前小时的开始时间点，最大时间范围为1小时-订单创建时间
    :param offset: 分页模式使用，默认为0
    :param limit: 分页模式使用，默认100，最大值1000
    :param device_id: 用户设备id
    :param outside_trade_no: 第三方订单号
    :param paid: 是否支付成功
    :param optimizer_account: 优化师邮箱（不可使用主管账户邮箱请求）
    :param open_id: 用户微信open_id
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }

    url = 'https://www.changdunovel.com/novelsale/openapi/user/recharge/v1'
    if begin is not None:
        params['begin'] = begin
    if end is not None:
        params['end'] = end
    if offset is not None:
        params['offset'] = offset
    if limit is not None:
        params['limit'] = limit
    if device_id is not None:
        params['device_id'] = device_id
    if outside_trade_no is not None:
        params['outside_trade_no'] = outside_trade_no
    if paid is not None:
        params['paid'] = paid
    if optimizer_account is not None:
        params['optimizer_account'] = optimizer_account
    if open_id is not None:
        params['open_id'] = open_id

    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True
    )


def get_user_read(
        distributor_id,
        secret_key,
        device_id=None,
        begin_time=None,
        end_time=None,
        page_size=None,
        page_index=None,
        optimizer_account=None,
        open_id=None
):
    """
    获取用户阅读进度
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥
    :param device_id: 用户ID
    :param begin_time: 开始时间
    :param end_time: 结束时间
    :param page_size: 每页大小
    :param page_index: 页码，从0开始
    :param optimizer_account: 优化师邮箱
    :param open_id: 用户微信open_id
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }

    url = 'https://www.changdunovel.com/novelsale/openapi/user/read/list/v1/'
    if device_id is not None:
        params['device_id'] = device_id
    if begin_time is not None:
        params['begin_time'] = begin_time
    if end_time is not None:
        params['end_time'] = end_time
    if page_size is not None:
        params['page_size'] = page_size
    if page_index is not None:
        params['page_index'] = page_index
    if optimizer_account is not None:
        params['optimizer_account'] = optimizer_account
    if open_id is not None:
        params['open_id'] = open_id
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True
    )


def get_package_info(
        distributor_id,
        secret_key
):
    """
    获取可用快应用/公众号列表
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }

    url = 'https://www.changdunovel.com/novelsale/openapi/package_info/v1/'
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True
    )


def get_purchase(
        distributor_id,
        secret_key,
        book_id=None,
        promotion_id=None,
        device_id=None,
        begin=None,
        end=None,
        offset=None,
        limit=None,
        optimizer_account=None,
        open_id=None
):
    """
    获取用户消费记录
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥

    :param book_id: 书籍id
    :param promotion_id: 推广链id
    :param device_id: 用户设备id
    :param begin:
    :param end:
    :param offset:
    :param limit:
    :param optimizer_account: 优化师邮箱
    :param open_id: 微信open_id
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }
    if book_id is not None:
        params['book_id'] = book_id
    if promotion_id is not None:
        params['promotion_id'] = promotion_id
    if device_id is not None:
        params['device_id'] = device_id
    if begin is not None:
        params['begin'] = begin
    if end is not None:
        params['end'] = end
    if offset is not None:
        params['offset'] = offset
    if limit is not None:
        params['limit'] = limit
    if optimizer_account is not None:
        params['optimizer_account'] = optimizer_account
    if open_id is not None:
        params['open_id'] = open_id

    url = 'https://www.changdunovel.com/novelsale/openapi/user/purchase/v1/'
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True
    )


def get_user(
        distributor_id,
        secret_key,
        media_source=None,
        book_source=None,
        promotion_id=None,
        show_not_recharge=None,
        page_size=None,
        page_index=None,
        optimizer_account=None,
        begin_time: int = None,
        end_time: int = None,
        open_id=None
):
    """
    获取用户信息接口
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥

    :param media_source: 1 为字节/ 2为腾讯
    :param book_source: 书籍来源
    :param promotion_id: 推广链来源
    :param show_not_recharge: true 展示所有用户; false/不传 只展示充值用户
    :param page_size: 每页大小
    :param page_index: 页码，从0开始
    :param optimizer_account: 优化师邮箱
    :param begin_time: 开始时间（注册/染色时间）
    :param end_time: 结束时间（注册/染色时间）
    :param open_id: 用户微信open_id
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }
    if media_source is not None:
        params['media_source'] = media_source
    if book_source is not None:
        params['book_source'] = book_source
    if promotion_id is not None:
        params['promotion_id'] = promotion_id
    if show_not_recharge is not None:
        params['show_not_recharge'] = show_not_recharge
    if page_size is not None:
        params['page_size'] = page_size
    if page_index is not None:
        params['page_index'] = page_index
    if optimizer_account is not None:
        params['optimizer_account'] = optimizer_account
    if begin_time is not None:
        params['begin_time'] = begin_time
    if end_time is not None:
        params['end_time'] = end_time
    if open_id is not None:
        params['open_id'] = open_id

    url = 'https://www.changdunovel.com/novelsale/openapi/user/list/v1/'
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True
    )


def get_book_meta(
        distributor_id,
        secret_key,
        book_id=None
):
    """
    获取书籍信息 接口
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥

    :param book_id: 书id
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }
    if book_id is not None:
        params['book_id'] = book_id

    url = 'https://www.changdunovel.com/novelsale/openapi/content/book_meta/v1/'
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True
    )
