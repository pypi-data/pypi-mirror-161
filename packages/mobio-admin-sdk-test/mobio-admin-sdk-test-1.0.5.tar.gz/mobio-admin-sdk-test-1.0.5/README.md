##  Thư viện Admin SDK dành cho các module.


### Cài đặt:
```bash
 $ pip3 install mobio-admin-sdk
 ```

### Chức năng:
* Verify token 


### Sử dụng:

##### 1. Verify token:
   ```python
    from mobio.sdks.admin import MobioAdminSDK

    MobioAdminSDK().config(
        admin_host="",	# admin host
        redis_uri="",	# redis uri
        module_use="",	# liên hệ admin để khai báo tên của module
        module_encrypt="",	# liên hệ admin để lấy mã
        api_admin_version="api/v2.1",   # danh sách api có thể sử dụng ["v1.0", "api/v2.0", "api/v2.1"]
    )
    auth = MobioAdminSDK().create_mobio_verify_token()
    
    @service_mod.route(url_path, methods=["get"])
    @auth.verify_token
    @try_catch_error
    def get_config(merchant_id):
        return build_response_message(Config(merchant_id).get_data())
   ```

##### 2. Merchant config:
   ```python
    from mobio.sdks.admin import MobioAdminSDK

    MobioAdminSDK().request_get_merchant_config_host(
            merchant_id,
            key=None,       # key muốn lấy giá trị
            admin_version=None, # api version admin muốn gọi trong trường hợp chỉ có version đó hỗ trợ
        )
    MobioAdminSDK().request_get_merchant_config_other(
            merchant_id,
            list_key=None,       # danh sách key muốn lấy giá trị
            admin_version=None, # api version admin muốn gọi trong trường hợp chỉ có version đó hỗ trợ
        )
    MobioAdminSDK().request_check_merchant_is_brand(
            merchant_id,
            admin_version=None, # api version admin muốn gọi trong trường hợp chỉ có version đó hỗ trợ
            token_value=None,  # token_value dạng là Bearer hoặc Basic, nếu nơi gọi là request đã authen thì 
                                # không cần truyền, token_value sẽ lấy từ header của request 
        )
    MobioAdminSDK().request_get_info_staff(
            merchant_id,
            account_id,
            admin_version=None, # api version admin muốn gọi trong trường hợp chỉ có version đó hỗ trợ
            token_value=None,  # token_value dạng là Bearer hoặc Basic, nếu nơi gọi là request đã authen thì
                                # không cần truyền, token_value sẽ lấy từ header của request
        )
    MobioAdminSDK().request_get_list_info_staff(
            merchant_id,
            params=None, # tham số của api  VD: {"per_page": -1}
            admin_version=None, # api version admin muốn gọi trong trường hợp chỉ có version đó hỗ trợ
            token_value=None,  # token_value dạng là Bearer hoặc Basic, nếu nơi gọi là request đã authen thì
                                # không cần truyền, token_value sẽ lấy từ header của request
        )
    MobioAdminSDK().request_get_list_parent_merchant(
            merchant_id,
            admin_version=None, # api version admin muốn gọi trong trường hợp chỉ có version đó hỗ trợ
            token_value=None,  # token_value dạng là Bearer hoặc Basic, nếu nơi gọi là request đã authen thì
                                # không cần truyền, token_value sẽ lấy từ header của request
        )
    MobioAdminSDK().request_get_list_profile_group(
            merchant_id=None,
            params=None,
            admin_version=None, # api version admin muốn gọi trong trường hợp chỉ có version đó hỗ trợ
            token_value=None,  # token_value dạng là Bearer hoặc Basic, nếu nơi gọi là request đã authen thì
                                # không cần truyền, token_value sẽ lấy từ header của request
        )
    MobioAdminSDK().request_get_list_sub_brand(
            params=None,        # tham số của api  VD: {"merchant_id": ""}
            admin_version=None, # api version admin muốn gọi trong trường hợp chỉ có version đó hỗ trợ
            token_value=None,  # token_value dạng là Bearer hoặc Basic, nếu nơi gọi là request đã authen thì
                                # không cần truyền, token_value sẽ lấy từ header của request
        )
    MobioAdminSDK().request_get_info_sub_brand(
            subbrand_id=None,
            admin_version=None, # api version admin muốn gọi trong trường hợp chỉ có version đó hỗ trợ
            token_value=None,  # token_value dạng là Bearer hoặc Basic, nếu nơi gọi là request đã authen thì
                                # không cần truyền, token_value sẽ lấy từ header của request
        )
    MobioAdminSDK().request_get_partner_info(
            partner_key=None,
            decrypt_data=False,
    )   # result: { "code": 200, "data": ""}, {"code": 400, "message": "key not found"}, {"code": 412, "message": "key not active"}, {"code": 413, "message": "key expire"}
        



```
##### 3. Save log action account:
   ```python
    from mobio.sdks.admin import MobioAdminSDK
    action_account = {
            'account_id': "uuid",# required
            'action_name_vi': 'action name',# required
            'action_name_en': 'action name',# required
            'merchant_id': "uuid",# required
            'created_time': 0129301293  # required (timestamp(utcnow))
        }
    MobioAdminSDK().admin_save_log_action_account(action_account)
   ```
#### Log - 1.0.1
    - release sdk
#### Log - 1.0.2
    - Kiểm tra license server còn hạn sử dụng hay không 
#### Log - 1.0.3
    - Fix lỗi đọc file license 
#### Log - 1.0.4
    - Authen app key data out 
#### Log - 1.0.5
    - update lib kafka v2
#### Log - 1.0.6
    - encrypt, decrypt field by config
    