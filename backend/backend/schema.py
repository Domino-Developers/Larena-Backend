import graphene
import graphql_jwt

import ecommerce.schema


class Query(ecommerce.schema.Query, graphene.ObjectType):
    pass


class Mutation(graphene.ObjectType):
    # root mutations
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
