import re
import pandas as pd



def cleanedField(request, SYM):
    return SYM.app('pipedrive').update_deal_cleanedField(1)


def get_deals_notCleaned(request, SYM):
    return SYM.app('pipedrive').get_deals_notCleaned()


def get_deal(request, SYM):
    return SYM.app('pipedrive').get_deal_related_objects(1)


def clean(request, SYM):
    deals = SYM.app('pipedrive').get_deals_notCleaned()
    for deal in deals:
        print("deal: ", deal)
        deal_id = deal['id']
        deal_related_objects = SYM.app('pipedrive').get_deal_related_objects(deal_id)
        try:
            deal_related_objects["person"]
        except:
            deal_related_objects["person"] = None
        if deal_related_objects["person"]:
            deal_person = deal_related_objects["person"]
            person_id = deal['person_id']['value']
        else:
            deal_person = None
            person_id = None
        try:
            company_id = deal['org_id']['value']
        except:
            company_id = None
        try:
            deal_related_objects["organization"]
        except:
            deal_related_objects["organization"] = None
        if deal_related_objects["organization"]:
            deal_company = deal_related_objects["organization"]
            comp_keys = list(deal_company.keys())
            company_members = deal_company[comp_keys[0]]["people_count"]
        else:
            deal_company = None
            company_members = None
        data = ""
        deal_pipeline =deal_related_objects["pipeline"]
        pipe_keys = list(deal_pipeline.keys())
        pipe_name = deal_pipeline[pipe_keys[0]]["name"]

        # company_members = SYM.app('pipedrive').get_organization_details(company_id)["people_count"]
        if deal_person != None:
            if len(deal['person_id']['phone']) > 1:
                deal_phone = [x['value'] for x in deal['person_id']['phone']]
            else:
                deal_phone = deal['person_id']['phone'][0]['value']
            print("deal_phone: ", deal_phone)
        # if deal_company != None:
            if len(deal['person_id']['email']) > 1:
                deal_email = [x['value'] for x in deal['person_id']['email']]
            else:
                deal_email = deal['person_id']['email'][0]['value']
            print("deal_email: ", deal_email)

        print("company_members: ", company_members)

        if deal_person == None:
            """insert problem deal_id"""
            problem = f"deal_id: {deal_id} - deal_person: {deal_person} - deal_company: {deal_company}"
            SYM.app('postgre').insert_problem_deal_id(deal_id, problem)

        elif deal_company == None:
            """insert problem deal_id"""
            problem = f"deal_id: {deal_id} - deal_person: {deal_person} - deal_company: {deal_company}"
            SYM.app('postgre').insert_problem_deal_id(deal_id, problem)

        elif len(deal_person) > 1 or len(deal_company) > 1 or company_members > 2 or company_members == 0:
            """insert problem deal_id"""
            problem = f"company_members: {company_members}"
            SYM.app('postgre').insert_problem_deal_id(deal_id, problem)
        
        elif SYM.app('postgre').read_account_business_from_pipedriveID(deal_id) != []:
            data = SYM.app('postgre').read_account_business_from_pipedriveID(deal_id)[0]
            """update pipe_business"""
            SYM.app('pipedrive').update_person_from_account_business(person_id, data)
            SYM.app('pipedrive').update_organization_from_account_business(company_id, data)
            try:
                SYM.app('postgre').insert_link_account(data[0], person_id)
            except:
                pass
            try:
                SYM.app('postgre').insert_link_business(data[6], company_id)
            except:
                pass
            if SYM.app('postgre').read_link_business_deal_from_business_id(data[6]) == []:
                SYM.app('postgre').insert_link_business_deal(data[6], deal_id, pipe_name)
            else:
                existing_deal = SYM.app('postgre').read_link_business_deal_from_business_id(data[6])[0]
                existing_deal_pipe_name = existing_deal[2]
                existing_deal_id = existing_deal[1]
                if existing_deal_pipe_name == pipe_name == 'OUTBOUND NEW':
                    problem = f"deal_id: {deal_id} - pipe_name: {pipe_name} - existing_deal_id: {existing_deal_id} - existing_deal_pipe_name: {existing_deal_pipe_name}"
                    SYM.app('postgre').insert_problem_deal_id(deal_id, problem)
                    SYM.app('postgre').insert_problem_deal_id(existing_deal_id, problem)
                    SYM.app('postgre').remove_link_business_deal(deal_id)
                    SYM.app('postgre').remove_link_business_deal(existing_deal_id)
                elif existing_deal_pipe_name != pipe_name:
                    if existing_deal_pipe_name == 'OUTBOUND NEW':
                        # Merge deal with existing deal as parent
                        SYM.app('pipedrive').merge_deal(deal_id, existing_deal_id)
                        # SYM.app('postgre').update_link_business_deal(deal_id, existing_deal_id)
                        deal_id = existing_deal_id
                    elif pipe_name == 'OUTBOUND NEW':
                        # Merge deal with existing deal as child
                        SYM.app('pipedrive').merge_deal(existing_deal_id, deal_id)
                        SYM.app('postgre').update_link_business_deal(existing_deal_id, deal_id, pipe_name)
                    else:
                        # Merge deal with existing deal as parent
                        SYM.app('pipedrive').merge_deal(existing_deal_id, deal_id)
                        SYM.app('postgre').update_link_business_deal(existing_deal_id, deal_id, pipe_name)
                # SYM.app('postgre').insert_link_business_deal(data[6], deal_id, pipe_name)

        elif deal_email:
            if type(deal_email) != list:
                deal_email = [deal_email]
            print("deal_email: ", deal_email)
            for email in deal_email:
                if SYM.app('postgre').read_account_business_from_email(email) != []:
                    data = SYM.app('postgre').read_account_business_from_email(email)[0]
                    print("data: ", data)
                    """update pipe_business"""
                    SYM.app('pipedrive').update_person_from_account_business(person_id, data)
                    SYM.app('pipedrive').update_organization_from_account_business(company_id, data)
                    try:
                        SYM.app('postgre').insert_link_account(data[0], person_id)
                    except:
                        pass
                    try:
                        SYM.app('postgre').insert_link_business(data[6], company_id)
                    except:
                        pass
                    if SYM.app('postgre').read_link_business_deal_from_business_id(data[6]) == []:
                        SYM.app('postgre').insert_link_business_deal(data[6], deal_id, pipe_name)
                    else:
                        existing_deal = SYM.app('postgre').read_link_business_deal_from_business_id(data[6])[0]
                        existing_deal_pipe_name = existing_deal[2]
                        existing_deal_id = existing_deal[1]
                        if existing_deal_pipe_name == pipe_name == 'OUTBOUND NEW':
                            problem = f"deal_id: {deal_id} - pipe_name: {pipe_name} - existing_deal_id: {existing_deal_id} - existing_deal_pipe_name: {existing_deal_pipe_name}"
                            SYM.app('postgre').insert_problem_deal_id(deal_id, problem)
                            SYM.app('postgre').insert_problem_deal_id(existing_deal_id, problem)
                            SYM.app('postgre').remove_link_business_deal(deal_id)
                            SYM.app('postgre').remove_link_business_deal(existing_deal_id)
                        elif existing_deal_pipe_name != pipe_name:
                            if existing_deal_pipe_name == 'OUTBOUND NEW':
                                # Merge deal with existing deal as parent
                                SYM.app('pipedrive').merge_deal(deal_id, existing_deal_id)
                                # SYM.app('postgre').update_link_business_deal(deal_id, existing_deal_id)
                                deal_id = existing_deal_id
                            elif pipe_name == 'OUTBOUND NEW':
                                # Merge deal with existing deal as child
                                SYM.app('pipedrive').merge_deal(existing_deal_id, deal_id)
                                SYM.app('postgre').update_link_business_deal(existing_deal_id, deal_id, pipe_name)
                            else:
                                # Merge deal with existing deal as parent
                                SYM.app('pipedrive').merge_deal(existing_deal_id, deal_id)
                                SYM.app('postgre').update_link_business_deal(existing_deal_id, deal_id, pipe_name)
                        # SYM.app('postgre').insert_link_business_deal(data[6], deal_id, pipe_name)
                    break
                else:
                    """insert dont find deal_id"""
                    try:
                        SYM.app('postgre').insert_dont_find_deal_id(deal_id)
                    except:
                        pass
                    data = None
        
        elif deal_phone:
            
            if type(deal_phone) != list:
                deal_phone = [deal_phone]
            for phone in deal_phone:
                phone = re.sub("^0", "+33", phone)
                print("phone: ", phone)
                
                if SYM.app('postgre').read_account_business_from_phone(phone) != []:
                    data = SYM.app('postgre').read_account_business_from_phone(phone)[0]
                    """update pipe_business"""
                    SYM.app('pipedrive').update_person_from_account_business(person_id, data)
                    SYM.app('pipedrive').update_organization_from_account_business(company_id, data)
                    try:
                        SYM.app('postgre').insert_link_account(data[0], person_id)
                    except:
                        pass
                    try:
                        SYM.app('postgre').insert_link_business(data[6], company_id)
                    except:
                        pass
                    if SYM.app('postgre').read_link_business_deal_from_business_id(data[6]) == []:
                        SYM.app('postgre').insert_link_business_deal(data[6], deal_id, pipe_name)
                    else:
                        existing_deal = SYM.app('postgre').read_link_business_deal_from_business_id(data[6])[0]
                        existing_deal_pipe_name = existing_deal[2]
                        existing_deal_id = existing_deal[1]
                        if existing_deal_pipe_name == pipe_name == 'OUTBOUND NEW':
                            problem = f"deal_id: {deal_id} - pipe_name: {pipe_name} - existing_deal_id: {existing_deal_id} - existing_deal_pipe_name: {existing_deal_pipe_name}"
                            SYM.app('postgre').insert_problem_deal_id(deal_id, problem)
                            SYM.app('postgre').insert_problem_deal_id(existing_deal_id, problem)
                            SYM.app('postgre').remove_link_business_deal(deal_id)
                            SYM.app('postgre').remove_link_business_deal(existing_deal_id)
                        elif existing_deal_pipe_name != pipe_name:
                            if existing_deal_pipe_name == 'OUTBOUND NEW':
                                # Merge deal with existing deal as parent
                                SYM.app('pipedrive').merge_deal(deal_id, existing_deal_id)
                                # SYM.app('postgre').update_link_business_deal(deal_id, existing_deal_id)
                                deal_id = existing_deal_id
                            elif pipe_name == 'OUTBOUND NEW':
                                # Merge deal with existing deal as child
                                SYM.app('pipedrive').merge_deal(existing_deal_id, deal_id)
                                SYM.app('postgre').update_link_business_deal(existing_deal_id, deal_id, pipe_name)
                            else:
                                # Merge deal with existing deal as parent
                                SYM.app('pipedrive').merge_deal(existing_deal_id, deal_id)
                                SYM.app('postgre').update_link_business_deal(existing_deal_id, deal_id, pipe_name)
                        # SYM.app('postgre').insert_link_business_deal(data[6], deal_id, pipe_name)
                    break
                else:
                    """insert dont find deal_id"""
                    try:
                        SYM.app('postgre').insert_dont_find_deal_id(deal_id)
                    except:
                        pass
                    data = None

        else:
            """insert dont find deal_id"""
            try:
                SYM.app('postgre').insert_dont_find_deal_id(deal_id)
            except:
                pass

        print("deal_id: ", deal_id)
        print("deal_person: ", deal_person)
        print("deal_company: ", deal_company)
        print("person_id: ", person_id)
        print("company_id: ", company_id)
        print("data: ", data)
        print('')

        SYM.app('pipedrive').update_deal_cleanedField(deal_id)

    return "done"


def test(request, SYM):
    deals = SYM.app('pipedrive').get_all_deals()

    deal_list = []
    for deal in deals:
        # print("deal: ", deal)
        # break
        deal_list.append({
            "deal_id": deal["id"],
            "deal_title": deal["title"],
            "pipeline_id": deal["pipeline_id"],
            "person_name": deal["person_name"],
            "org_name": deal["org_name"],
        })
    df = pd.DataFrame(deal_list)
    duplicates = df[df.duplicated(subset=["person_name", "org_name"], keep=False)]

    if duplicates.empty:
        print("no duplicate")
        return "no duplicate"
    else:
        print(duplicates)
        return duplicates.to_json()
    
    # return "done"


def t(request, SYM):
    # print(SYM.app('postgre').read_link_business_deal(7))
    SYM.app('postgre').remove_link_business_deal(55)
    return "done"