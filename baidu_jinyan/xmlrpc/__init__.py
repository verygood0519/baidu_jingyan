from wordpress_xmlrpc import Client,WordPressPost,WordPressPage
from wordpress_xmlrpc.methods.posts import GetPosts,NewPost,GetPostTypes
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods.taxonomies import GetTaxonomies,GetTaxonomy,GetTerm,GetTerms
from wordpress_xmlrpc.methods.options import GetOptions
from wordpress_xmlrpc.methods.pages import GetPageTemplates
from wordpress_xmlrpc.methods.users import GetAuthors
from wordpress_xmlrpc.methods.media import GetMediaLibrary

def main():
    wp = Client('http://www.gggotravel.com/xmlrpc.php', 'admin', 'lyhAdmin123')
    for media in wp.call(GetMediaLibrary({'number':10})):
        print(media.link,media.title,media.parent,media.date_created)
    # print(wp.call(GetPageTemplates()))

    # for post in wp.call(GetPosts({'post_type': 'post'},results_class=WordPressPage)):
    #     print(post.terms)
    # for postType in wp.call(GetPostTypes()):
    #     print(postType)
    # for taxs in wp.call(GetTaxonomies()):
    #     print(taxs)
    # print(wp.call(GetTerms('category')))
    # print(wp.call(GetTaxonomy('category')))
    # print(wp.call(GetTerm('category',3)))
if __name__ == '__main__':
    main()