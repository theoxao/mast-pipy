1.服务部署到ecs  
2.zt网络调用树莓派   
3.树莓派心跳机制

流程： 1收到请求后，调用query_state查询当前设备状态 1.1若设备状态和请求状态一直，更新数据库value状态 1.2不一致调用update_state，再次query_state判断是否成功 1.2.1成功返回
1.2.2不成功，切换direction后再次调用update_state,