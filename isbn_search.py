import requests
import xml.etree.ElementTree as ET

def search_isbn_googlebooks(isbn):
    """Google Books APIでISBN検索"""
    isbn = isbn.replace('-', '').replace(' ', '')
    url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}'
    
    try:
        print(f'  URL: {url}')
        response = requests.get(url, timeout=10)
        print(f'  ステータスコード: {response.status_code}')
        response.raise_for_status()
        data = response.json()
        
        if data.get('totalItems', 0) > 0:
            item = data['items'][0]
            volume_info = item.get('volumeInfo', {})
            
            authors = volume_info.get('authors', [])
            author_str = ', '.join(authors) if authors else '情報なし'
            
            return {
                'title': volume_info.get('title', '情報なし'),
                'author': author_str,
                'publisher': volume_info.get('publisher', '情報なし'),
                'pubdate': volume_info.get('publishedDate', '情報なし'),
                'isbn': isbn,
                'description': volume_info.get('description', '')[:200] if volume_info.get('description') else '',
                'source': 'Google Books'
            }
        else:
            print('  データが見つかりませんでした')
    except Exception as e:
        print(f'  エラー: {e}')
    
    return None

def search_isbn_openbd(isbn):
    """openBD APIでISBN検索"""
    isbn = isbn.replace('-', '').replace(' ', '')
    url = f'https://api.openbd.jp/v1/get?isbn={isbn}'
    
    try:
        print(f'  URL: {url}')
        response = requests.get(url, timeout=10)
        print(f'  ステータスコード: {response.status_code}')
        response.raise_for_status()
        data = response.json()
        
        if data and data[0]:
            summary = data[0].get('summary', {})
            return {
                'title': summary.get('title', '情報なし'),
                'author': summary.get('author', '情報なし'),
                'publisher': summary.get('publisher', '情報なし'),
                'pubdate': summary.get('pubdate', '情報なし'),
                'isbn': summary.get('isbn', isbn),
                'description': '',
                'source': 'openBD'
            }
        else:
            print('  データが空でした')
    except Exception as e:
        print(f'  エラー: {e}')
    
    return None

def search_isbn_ndl(isbn):
    """国立国会図書館APIでISBN検索"""
    isbn = isbn.replace('-', '').replace(' ', '')
    url = f'https://iss.ndl.go.jp/api/sru?operation=searchRetrieve&query=isbn="{isbn}"&recordSchema=dcndl&maximumRecords=1'
    
    try:
        print(f'  URL: {url}')
        response = requests.get(url, timeout=10)
        print(f'  ステータスコード: {response.status_code}')
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        ns = {
            'srw': 'http://www.loc.gov/zing/srw/',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'dcterms': 'http://purl.org/dc/terms/'
        }
        
        num_records = root.find('.//srw:numberOfRecords', ns)
        print(f'  見つかったレコード数: {num_records.text if num_records is not None else 0}')
        
        if num_records is not None and int(num_records.text) > 0:
            record = root.find('.//srw:recordData', ns)
            if record is not None:
                title = record.find('.//dc:title', ns)
                creator = record.find('.//dc:creator', ns)
                publisher = record.find('.//dc:publisher', ns)
                date = record.find('.//dcterms:issued', ns)
                
                return {
                    'title': title.text if title is not None else '情報なし',
                    'author': creator.text if creator is not None else '情報なし',
                    'publisher': publisher.text if publisher is not None else '情報なし',
                    'pubdate': date.text if date is not None else '情報なし',
                    'isbn': isbn,
                    'description': '',
                    'source': '国立国会図書館'
                }
        else:
            print('  レコードが見つかりませんでした')
    except Exception as e:
        print(f'  エラー: {e}')
    
    return None

def search_isbn(isbn):
    """複数のAPIでISBN検索"""
    isbn = isbn.replace('-', '').replace(' ', '')
    
    print(f'\n🔍 ISBN {isbn} を検索中...')
    
    # Google Booksで検索
    print('\n[1] Google Booksで検索中...')
    result = search_isbn_googlebooks(isbn)
    
    # 見つからなければopenBDで検索
    if not result:
        print('\n[2] openBDで検索中...')
        result = search_isbn_openbd(isbn)
    
    # 見つからなければ国立国会図書館で検索
    if not result:
        print('\n[3] 国立国会図書館で検索中...')
        result = search_isbn_ndl(isbn)
    
    # 結果を表示
    if result:
        print('\n' + '='*50)
        print(f'📚 書誌情報 (データ提供: {result["source"]})')
        print('='*50)
        print(f'タイトル: {result["title"]}')
        print(f'著者: {result["author"]}')
        print(f'出版社: {result["publisher"]}')
        print(f'出版日: {result["pubdate"]}')
        print(f'ISBN: {result["isbn"]}')
        if result.get('description'):
            print(f'概要: {result["description"]}...')
        print('='*50 + '\n')
        return result
    else:
        print(f'\n❌ ISBN {isbn} の書籍が見つかりませんでした')
        print('※ すべてのデータベースで検索しましたが見つかりませんでした\n')
        return None

def main():
    """メイン処理"""
    print('='*50)
    print('📖 ISBN書誌情報検索プログラム (デバッグ版)')
    print('='*50)
    print('データ提供: Google Books + openBD + 国立国会図書館')
    print('終了するには "q" または "quit" と入力してください\n')
    
    while True:
        isbn = input('ISBNを入力してください: ').strip()
        
        if isbn.lower() in ['q', 'quit', 'exit']:
            print('\nプログラムを終了します')
            break
        
        if not isbn:
            print('❌ ISBNを入力してください')
            continue
        
        search_isbn(isbn)

if __name__ == '__main__':
    main()